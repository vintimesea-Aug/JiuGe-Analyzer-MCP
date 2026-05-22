"""Audio download from episode URL."""

import os
from pathlib import Path
from urllib.request import urlopen


class AudioDownloadError(Exception):
    """Failed to download audio."""


def _cache_dir() -> Path:
    d = Path(os.path.join(os.path.dirname(__file__), "..", "..", "data", "podcast_cache"))
    d.mkdir(parents=True, exist_ok=True)
    return d


def _find_existing(episode_id: str) -> Path | None:
    for ext in (".m4a", ".mp3"):
        p = _cache_dir() / f"{episode_id}{ext}"
        if p.exists() and p.stat().st_size > 1000:
            return p
    return None


def download_audio(audio_url: str, episode_id: str) -> Path:
    existing = _find_existing(episode_id)
    if existing:
        return existing

    url_lower = audio_url.lower().rstrip("/")
    if ".m4a" in url_lower or "m4a" in url_lower.split("?")[0].split(".")[-1]:
        ext = ".m4a"
    elif ".mp3" in url_lower or "mp3" in url_lower.split("?")[0].split(".")[-1]:
        ext = ".mp3"
    else:
        ext = ".m4a"

    dest = _cache_dir() / f"{episode_id}{ext}"
    try:
        with urlopen(audio_url, timeout=300) as src:
            with open(dest, "wb") as f:
                while True:
                    chunk = src.read(8192)
                    if not chunk:
                        break
                    f.write(chunk)
    except Exception as e:
        if dest.exists():
            dest.unlink()
        raise AudioDownloadError(f"Download failed: {e}")
    return dest


def cleanup_audio(episode_id: str) -> bool:
    audio = _find_existing(episode_id)
    if audio:
        audio.unlink()
        return True
    return False
