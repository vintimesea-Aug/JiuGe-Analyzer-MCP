"""Structured output schemas, prompt builders, and validation for podcast analysis."""

SCHEMA_VERSION = 1

FAST_REQUIRED = [
    "overview",
    "topic_classification",
    "core_arguments",
    "extended_thinking",
    "audience_guide",
    "overall_rating",
]

DEEP_REQUIRED = [
    "basic_info",
    "guest_profile",
    "core_arguments",
    "content_analysis",
    "future_outlook",
    "structural_insights",
    "critical_assessment",
    "overall_rating",
]


def _lang_instr(lang: str) -> tuple[str, str]:
    if lang == "en":
        return ("All analysis must be written in English.",
                "IMPORTANT: Write the entire analysis in English only.")
    return ("所有分析必须用中文输出。",
            "重要：全报告必须用中文撰写。")


def build_deep_system(lang: str) -> str:
    li, _ = _lang_instr(lang)
    return (
        f"You are a deep content analyst. Output a valid JSON object. {li} "
        "Every field must be filled with substantive content. "
        "Do not use placeholder text, empty strings, or 'N/A'. "
        "Array fields need at least 2 items. String fields need at least 3 sentences."
    )


def build_deep_user(meta: dict, transcript: str, lang: str) -> str:
    _, oli = _lang_instr(lang)
    epid = meta["episode_id"]
    title = meta.get("title", epid)
    podcast = meta.get("podcast_name", "-")
    host = meta.get("host", "-")
    dur = meta.get("duration", "-")
    pub = meta.get("pubDate", "-")

    max_chars = 200000
    if len(transcript) > max_chars:
        transcript = transcript[:max_chars] + "\n\n[...truncated...]"

    return f"""{oli}

Metadata:
- Podcast: {podcast}
- Title: {title}
- Host: {host}
- Duration: {dur}
- Published: {pub}
- URL: https://www.xiaoyuzhoufm.com/episode/{epid}

Generate a JSON object with this exact structure. Every field must be filled.
String fields: at least 3 sentences. Array fields: at least 2 items.

{{
  "schema_version": {SCHEMA_VERSION},
  "basic_info": {{
    "podcast": "...",
    "host": "...",
    "guests": ["..."],
    "duration": "{dur}",
    "published": "{pub}",
    "url": "https://www.xiaoyuzhoufm.com/episode/{epid}"
  }},
  "guest_profile": "3-5 paragraphs on guest background, expertise, style, limitations",
  "core_arguments": "1-2 paragraphs on central thesis",
  "content_analysis": [
    {{
      "layer": "topic name",
      "core_argument": "central proposition",
      "logic_chain": "how the argument is built",
      "evidence": "key proof points"
    }}
  ],
  "future_outlook": {{
    "short_term": "0-2 year",
    "mid_term": "2-5 year",
    "long_term": "5+ year"
  }},
  "structural_insights": ["at least 5 cross-domain observations"],
  "critical_assessment": {{
    "counter_arguments": "opposing views missed",
    "cross_examination": "weak points in reasoning",
    "verdict": "final value judgment"
  }},
  "overall_rating": {{
    "recommendation": 4,
    "best_audience": "who benefits most",
    "core_value": "single biggest takeaway",
    "shortcomings": "what could be improved"
  }}
}}

Full Transcript:
{transcript}"""


def build_fast_system(lang: str) -> str:
    li, _ = _lang_instr(lang)
    return (
        f"You are a deep content analyst. Output a valid JSON object. {li} "
        "Every field must be filled substantively. "
        "No placeholder text, empty strings, or 'N/A'."
    )


def build_fast_user(meta: dict, lang: str) -> str:
    _, oli = _lang_instr(lang)
    epid = meta["episode_id"]
    title = meta.get("title", epid)
    podcast = meta.get("podcast_name", "-")
    host = meta.get("host", "-")
    dur = meta.get("duration", "-")
    pub = meta.get("pubDate", "-")
    desc = (meta.get("description", "") or "")[:2000]
    play = meta.get("playCount", "-")
    cmt = meta.get("commentCount", "-")
    clap = meta.get("clapCount", "-")
    fav = meta.get("favoriteCount", "-")

    return f"""{oli}

Metadata:
- Podcast: {podcast}
- Title: {title}
- Host: {host}
- Duration: {dur}
- Published: {pub}
- Plays: {play} | Comments: {cmt} | Claps: {clap} | Favorites: {fav}
- URL: https://www.xiaoyuzhoufm.com/episode/{epid}

Description: {desc}

Generate a JSON object with this structure. Every field must be filled.
String fields: at least 2 sentences. Array fields: at least 2 items.

{{
  "schema_version": {SCHEMA_VERSION},
  "overview": {{
    "summary": "what the episode is about",
    "stance": "neutral|positive|critical",
    "knowledge_density": "high|medium|low"
  }},
  "topic_classification": {{
    "primary_field": "main discipline",
    "cross_disciplines": ["related field 1", "field 2"]
  }},
  "core_arguments": ["key takeaway 1", "takeaway 2", "takeaway 3"],
  "extended_thinking": "cross-domain discussion",
  "audience_guide": {{
    "who_should_listen": ["audience 1", "audience 2"],
    "prerequisites": ["background needed"],
    "best_scenarios": ["scenario 1", "scenario 2"]
  }},
  "overall_rating": {{
    "info_density": 3,
    "knowledge_gain": 3,
    "value": 3
  }}
}}"""


def validate(analysis: dict, required: list[str]) -> list[str]:
    """Returns list of validation errors. Empty list = valid."""
    errors = []
    if not isinstance(analysis, dict):
        return ["Output is not a JSON object"]

    for field in required:
        if field not in analysis:
            errors.append(f"Missing: '{field}'")
            continue
        val = analysis[field]
        if val is None:
            errors.append(f"Null field: '{field}'")
        elif isinstance(val, str) and not val.strip():
            errors.append(f"Empty string: '{field}'")
        elif isinstance(val, str) and len(val.split()) < 5:
            errors.append(f"Too short: '{field}' ({len(val.split())} words)")
        elif isinstance(val, (list, dict)) and not val:
            errors.append(f"Empty {type(val).__name__}: '{field}'")

    # Depth checks for nested fields (only if present and non-empty)
    or_ = analysis.get("overall_rating")
    if isinstance(or_, dict) and or_:
        for k in ("recommendation", "best_audience", "core_value", "shortcomings", "info_density", "knowledge_gain", "value"):
            val = or_.get(k)
            if val is not None and isinstance(val, str) and not val.strip():
                errors.append(f"Empty string: 'overall_rating.{k}'")

    fo = analysis.get("future_outlook")
    if isinstance(fo, dict) and fo:
        for p in ("short_term", "mid_term", "long_term"):
            if p in fo and isinstance(fo[p], str) and not fo[p].strip():
                errors.append(f"Empty string: 'future_outlook.{p}'")

    si = analysis.get("structural_insights")
    if isinstance(si, list) and si:
        if len(si) < 3:
            errors.append(f"'structural_insights' has {len(si)} items, need >= 3")

    ca = analysis.get("content_analysis")
    if isinstance(ca, list) and ca:
        if len(ca) < 2:
            errors.append(f"'content_analysis' has {len(ca)} items, need >= 2")

    return errors
