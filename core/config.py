"""LLM provider detection and configuration.

Auto-detect provider from environment variables (priority order):
1. DEEPSEEK_API_KEY  → DeepSeek
2. OPENAI_API_KEY    → OpenAI
3. LLM_API_KEY       → Custom (requires LLM_BASE_URL + LLM_MODEL)
4. None              → Ollama at localhost:11434
"""

import os


# ── API Key detection ──

def detect_provider() -> dict:
    """Return {api_key, base_url, default_model} for the best available provider."""

    if key := os.environ.get("DEEPSEEK_API_KEY", ""):
        return {
            "api_key": key,
            "base_url": os.environ.get("LLM_BASE_URL", "https://api.deepseek.com/v1"),
            "default_model": os.environ.get("LLM_MODEL", "deepseek-chat"),
        }

    if key := os.environ.get("OPENAI_API_KEY", ""):
        return {
            "api_key": key,
            "base_url": os.environ.get("LLM_BASE_URL", "https://api.openai.com/v1"),
            "default_model": os.environ.get("LLM_MODEL", "gpt-4o"),
        }

    if key := os.environ.get("LLM_API_KEY", ""):
        return {
            "api_key": key,
            "base_url": os.environ.get("LLM_BASE_URL", "http://localhost:11434/v1"),
            "default_model": os.environ.get("LLM_MODEL", "qwen3.5:9b"),
        }

    # Fallback: Ollama local
    return {
        "api_key": "ollama",
        "base_url": "http://localhost:11434/v1",
        "default_model": os.environ.get("OLLAMA_MODEL", "qwen3.5:9b"),
    }


# ── Output directory for analysis reports ──

def output_dir():
    """Where analysis reports are saved. Configurable via JIUGE_OUTPUT_DIR env var.
    Default: data/analysis/ (project-relative).
    """
    default = os.path.join(os.path.dirname(__file__), "..", "data", "analysis")
    path = os.environ.get("JIUGE_OUTPUT_DIR", default)
    os.makedirs(path, exist_ok=True)
    return path


# ── Language ──

def report_language() -> str:
    return os.environ.get("REPORT_LANGUAGE", "zh")


def report_lang_name() -> str:
    return "en" if report_language() == "en" else "zh"


# ── Token limits ──

MAX_TOKENS_DEFAULT = 16384
MAX_TOKENS_REPORT = 32768
