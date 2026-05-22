"""Cache and file instead management for episode data."""

import json
import os
import re
from pathlib import Path

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


def save_analysis(episode_id: str, content: str) -> None:
    p = _key(f"{episode_id}_analysis.md")
    p.write_text(content, encoding="utf-8")


def load_analysis(episode_id: str) -> str | None:
    p = _key(f"{episode_id}_analysis.md")
    if not p.exists():
        return None
    return p.read_text(encoding="utf-8")


def save_analysis_file(episode_id: str, podcast_name: str, title: str, mode: str, content: str) -> Path:
    """Save analysis to human-readable file in output directory. Returns path."""
    from core.config import output_dir
    mode_tag = "深度" if "deep" in mode else "快速"
    safe_name = _sanitize(f"九歌{mode_tag}分析_{podcast_name}_{title}")
    out = Path(output_dir()) / f"{safe_name}_{episode_id}.md"
    out.write_text(content, encoding="utf-8")
    return out
