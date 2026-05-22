"""Cache and file instead management for episode data."""

import json
import os
import re
from pathlib import Path

from core.schema import SCHEMA_VERSION

CACHE_DIR = Path(os.path.join(os.path.dirname(__file__), "..", "data", "podcast_cache"))
CACHE_DIR.mkdir(parents=True, exist_ok=True)


def _key(name: str) -> Path:
    return CACHE_DIR / name


def save_meta(episode_id: str, meta: dict) -> None:
    p = _key(f"{episode_id}_meta.json")
    p.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")


def load_meta(episode_id: str) -> dict | None:
    p = _key(f"{episode_id}_meta.json")
    if not p.exists():
        return None
    return json.loads(p.read_text(encoding="utf-8"))


def _sanitize(name: str, max_len: int = 80) -> str:
    name = re.sub(r'[<>:"/\\|?*]', "_", name).strip()
    return name[:max_len].rstrip("_") if len(name) > max_len else name


def analysis_cache_key(episode_id: str, lang: str, suffix: str = "") -> str:
    """Generate cache key with schema version for automatic invalidation."""
    return f"{episode_id}_{lang}{suffix}_v{SCHEMA_VERSION}"


def save_analysis(cache_key: str, content: dict) -> None:
    p = _key(f"{cache_key}_analysis.json")
    p.write_text(json.dumps(content, ensure_ascii=False, indent=2), encoding="utf-8")


def load_analysis(cache_key: str) -> dict | None:
    p = _key(f"{cache_key}_analysis.json")
    if not p.exists():
        return None
    return json.loads(p.read_text(encoding="utf-8"))


def save_analysis_file(episode_id: str, podcast_name: str, title: str, mode: str, content: dict) -> Path:
    """Save analysis to readable JSON file. Returns path."""
    from core.config import output_dir
    mode_tag = "深度" if "deep" in mode else "快速"
    safe_name = _sanitize(f"九歌{mode_tag}分析_{podcast_name}_{title}")
    out = Path(output_dir()) / f"{safe_name}_{episode_id}.json"
    out.write_text(json.dumps(content, ensure_ascii=False, indent=2), encoding="utf-8")
    return out
