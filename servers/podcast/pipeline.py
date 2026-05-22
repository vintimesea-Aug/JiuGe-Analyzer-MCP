"""Podcast analysis pipeline — fast (metadata) and deep (transcript) paths."""

from core.llm import call_llm_json
from core.config import report_language
from core.cache import (
    save_meta, load_meta,
    save_analysis, load_analysis, save_analysis_file, analysis_cache_key,
)
from core.schema import (
    SCHEMA_VERSION,
    build_deep_system, build_deep_user,
    build_fast_system, build_fast_user,
    validate, DEEP_REQUIRED, FAST_REQUIRED,
)
from servers.podcast.fetcher import parse_episode_id, fetch_episode_detail
from servers.podcast.audio import download_audio
from servers.podcast.transcribe import transcribe, find_transcript

MAX_RETRIES = 2


def _ensure_meta(url: str) -> tuple[str, dict]:
    episode_id = parse_episode_id(url)
    meta = load_meta(episode_id)
    if not meta:
        meta = fetch_episode_detail(episode_id)
        save_meta(episode_id, meta)
    return episode_id, meta


def _analyze(
    episode_id: str, meta: dict, lang: str,
    build_system_fn, build_user_fn, required_fields: list,
    suffix: str,
) -> dict:
    ck = analysis_cache_key(episode_id, lang, suffix)
    cached = load_analysis(ck)
    if cached:
        return cached

    system = build_system_fn(lang)
    prompt = build_user_fn(meta, lang)
    errors = ["first try"]

    for attempt in range(1 + MAX_RETRIES):
        try:
            result = call_llm_json(system, prompt)
        except ValueError:
            result = {"error": "LLM call failed", "schema_version": SCHEMA_VERSION}
            break

        if not isinstance(result, dict):
            result = {"error": "LLM did not return a JSON object", "schema_version": SCHEMA_VERSION}
            break

        result.setdefault("schema_version", SCHEMA_VERSION)
        errors = validate(result, required_fields)
        if not errors:
            save_analysis(ck, result)
            return result

        if attempt < MAX_RETRIES:
            prompt += (
                f"\n\nPrevious attempt had validation errors: {errors}"
                "\nPlease fix ALL errors and return a complete JSON object."
            )

    result.setdefault("validation_errors", errors)
    save_analysis(ck, result)
    return result


def analyze_episode(url: str, lang: str = "") -> dict:
    """Fast path: metadata-only analysis (~30s). Returns {"file": Path, "summary": str}."""
    if not lang:
        lang = report_language()
    episode_id, meta = _ensure_meta(url)
    analysis = _analyze(
        episode_id, meta, lang,
        build_fast_system, build_fast_user, FAST_REQUIRED,
        suffix="",
    )
    out = save_analysis_file(
        episode_id, meta.get("podcast_name", ""), meta.get("title", ""), "fast", analysis,
    )
    errs = analysis.get("validation_errors", [])
    status = f"[OK] 快速分析完成 (含 {len(analysis)} 个字段)"
    if errs:
        status += f" [警告: {len(errs)} 个验证问题]"
    return {"file": str(out), "summary": status}


def analyze_episode_deep(url: str, lang: str = "") -> dict:
    """Deep path: download + transcribe + full transcript analysis. Returns {"file": Path, "summary": str}."""
    if not lang:
        lang = report_language()
    episode_id, meta = _ensure_meta(url)

    transcript_path = find_transcript(episode_id)
    if not transcript_path:
        audio_url = meta.get("audio_url", "")
        if not audio_url:
            raise ValueError("No audio URL available for this episode")
        audio_path = download_audio(audio_url, episode_id)
        transcript_path = transcribe(audio_path, episode_id)
    transcript = transcript_path.read_text(encoding="utf-8")

    def _build_user(m, lang):
        return build_deep_user(m, transcript, lang)

    analysis = _analyze(
        episode_id, meta, lang,
        build_deep_system, _build_user, DEEP_REQUIRED,
        suffix="_deep",
    )
    out = save_analysis_file(
        episode_id, meta.get("podcast_name", ""), meta.get("title", ""), "deep", analysis,
    )
    errs = analysis.get("validation_errors", [])
    status = f"[OK] 深度分析完成 (含 {len(analysis)} 个字段)"
    if errs:
        status += f" [警告: {len(errs)} 个验证问题]"
    return {"file": str(out), "summary": status}
