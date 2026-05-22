"""Podcast analysis pipeline — fast (metadata) and deep (transcript) paths."""

from core.llm import call_llm_report
from core.config import report_language
from core.cache import save_meta, load_meta, save_analysis, load_analysis, save_analysis_file
from servers.podcast.fetcher import parse_episode_id, fetch_episode_detail
from servers.podcast.audio import download_audio
from servers.podcast.transcribe import transcribe, find_transcript


def _lang_prefix(lang: str) -> tuple[str, str]:
    """Return (system_prompt_lang_instruction, output_lang_instruction)."""
    if lang == "en":
        return (
            "All analysis must be written in English.",
            "IMPORTANT: Write the entire report in English only.",
        )
    return (
            "所有分析必须用中文输出。",
            "重要：全报告必须用中文撰写。",
        )


def _build_prompt(meta: dict, lang: str) -> str:
    epid = meta["episode_id"]
    _, out_lang = _lang_prefix(lang)
    title = meta.get("title", meta["episode_id"])
    podcast = meta.get("podcast_name", "-")
    host = meta.get("host", "-")
    duration = meta.get("duration", "-")
    pub_date = meta.get("pubDate", "-")
    desc = (meta.get("description", "") or "")[:2000]
    play = meta.get("playCount", "-")
    comment = meta.get("commentCount", "-")
    clap = meta.get("clapCount", "-")
    fav = meta.get("favoriteCount", "-")

    return f"""{out_lang}

Metadata:
- Podcast: {podcast}
- Title: {title}
- Host: {host}
- Duration: {duration}
- Published: {pub_date}
- Plays: {play} | Comments: {comment} | Claps: {clap} | Favorites: {fav}
- URL: https://www.xiaoyuzhoufm.com/episode/{epid}

Description: {desc}

Generate a structured analysis report with sections:
1. Overview — what this episode is about, stance, knowledge density
2. Topic Classification — field and cross-disciplines
3. Core Arguments — key takeaways from title and description
4. Extended Thinking — cross-domain discussion based on the topic
5. Audience Guide — who should listen, prerequisites, best listening scenarios
6. Overall Rating — info density /5, knowledge gain /5, value /5
"""


def _build_deep_prompt(meta: dict, transcript: str, lang: str) -> str:
    epid = meta["episode_id"]
    _, out_lang = _lang_prefix(lang)
    max_chars = 200000
    if len(transcript) > max_chars:
        transcript = transcript[:max_chars] + "\n\n[...truncated...]"

    title = meta.get("title", meta["episode_id"])
    podcast = meta.get("podcast_name", "-")
    host = meta.get("host", "-")
    duration = meta.get("duration", "-")
    pub_date = meta.get("pubDate", "-")
    play = meta.get("playCount", "-")
    comment = meta.get("commentCount", "-")
    clap = meta.get("clapCount", "-")
    fav = meta.get("favoriteCount", "-")

    return f"""{out_lang}

Metadata:
- Podcast: {podcast}
- Title: {title}
- Host: {host}
- Duration: {duration}
- Published: {pub_date}
- Plays: {play} | Comments: {comment} | Claps: {clap} | Favorites: {fav}
- URL: https://www.xiaoyuzhoufm.com/episode/{epid}

Generate a deep structured analysis report with ALL of the following sections:

# Deep Podcast Analysis: {title}

## Basic Info
- Podcast, Host, Guest(s), Duration, Published, Listen link

## Guest Profile
3-5 paragraphs analyzing the guest's background, expertise, style, limitations.

## Core Arguments
1-2 paragraphs summarizing the episode's central thesis.

## Detailed Content Analysis
Break down into 3-6 topic layers. Each layer: core argument, logic chain, key evidence summary.

## Future Outlook
Short-term (0-2yr), Mid-term (2-5yr), Long-term (5yr+)

## Structural Insights
At least 5 cross-domain observations.

## Critical Assessment
Adversarial review: counter-arguments, cross-examination, verdict.

## Overall Rating
Recommendation /5 — best audience, core value, shortcomings.

---

## Full Transcript

<source type="web" trust="untrusted">
{transcript}
</source>"""


def _ensure_meta(url: str) -> tuple[str, dict]:
    episode_id = parse_episode_id(url)
    meta = load_meta(episode_id)
    if not meta:
        meta = fetch_episode_detail(episode_id)
        save_meta(episode_id, meta)
    return episode_id, meta


def _cache_key(episode_id: str, lang: str, suffix: str = "") -> str:
    return f"{episode_id}_{lang}{suffix}"


def analyze_episode(url: str, lang: str = "") -> dict:
    """Fast path: metadata-only analysis (~30s). Returns {"file": Path, "summary": str}."""
    if not lang:
        lang = report_language()
    episode_id, meta = _ensure_meta(url)
    ck = _cache_key(episode_id, lang)
    cached = load_analysis(ck)
    if cached:
        analysis = cached
    else:
        lang_instr, _ = _lang_prefix(lang)
        system = f"You are a deep content analyst. Generate a high-quality structured analysis report based on podcast metadata. {lang_instr}"
        prompt = _build_prompt(meta, lang)
        analysis = call_llm_report(system, prompt)
        save_analysis(ck, analysis)

    out = save_analysis_file(episode_id, meta.get("podcast_name", ""), meta.get("title", ""), "fast", analysis)
    return {"file": str(out), "summary": f"[OK] 快速分析完成 ({len(analysis)} 字)"}


def analyze_episode_deep(url: str, lang: str = "") -> dict:
    """Deep path: download + transcribe + full transcript analysis. Returns {"file": Path, "summary": str}."""
    if not lang:
        lang = report_language()
    episode_id, meta = _ensure_meta(url)

    ck = _cache_key(episode_id, lang, "_deep")
    cached = load_analysis(ck)
    if cached:
        analysis = cached
    else:
        transcript_path = find_transcript(episode_id)
        if not transcript_path:
            audio_url = meta.get("audio_url", "")
            if not audio_url:
                raise ValueError("No audio URL available for this episode")
            audio_path = download_audio(audio_url, episode_id)
            transcript_path = transcribe(audio_path, episode_id)
        transcript = transcript_path.read_text(encoding="utf-8")
        lang_instr, _ = _lang_prefix(lang)
        system = f"You are a deep content analyst. Generate a deep structured analysis report based on podcast transcript and metadata. {lang_instr}"
        prompt = _build_deep_prompt(meta, transcript, lang)
        analysis = call_llm_report(system, prompt)
        save_analysis(ck, analysis)

    out = save_analysis_file(episode_id, meta.get("podcast_name", ""), meta.get("title", ""), "deep", analysis)
    return {"file": str(out), "summary": f"[OK] 深度分析完成 ({len(analysis)} 字)"}
