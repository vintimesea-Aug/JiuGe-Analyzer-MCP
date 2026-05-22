"""Whisper transcription for podcast audio."""

import os
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
os.environ["no_proxy"] = "*"
os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"


def _cache_dir() -> Path:
    d = Path(os.path.join(os.path.dirname(__file__), "..", "..", "data", "podcast_cache"))
    d.mkdir(parents=True, exist_ok=True)
    return d


def find_transcript(episode_id: str) -> Path | None:
    p = _cache_dir() / f"{episode_id}_transcript.txt"
    if p.exists() and p.stat().st_size > 100:
        return p
    return None


def transcribe(audio_path: str | Path, episode_id: str, model_size: str = "tiny") -> Path:
    """Run faster-whisper on audio, return transcript path."""
    from faster_whisper import WhisperModel

    audio_path = str(audio_path)
    model = WhisperModel(model_size, device="cpu", compute_type="int8",
                         cpu_threads=4, num_workers=2)
    segments, _info = model.transcribe(
        audio_path, beam_size=1, language="zh",
        condition_on_previous_text=False,
    )

    out_path = _cache_dir() / f"{episode_id}_transcript.txt"
    with open(out_path, "w", encoding="utf-8") as f:
        for seg in segments:
            f.write(f"[{seg.start:.0f}s-{seg.end:.0f}s] {seg.text.strip()}\n")

    return out_path
