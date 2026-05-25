"""Textbook server configuration.

Cross-project dependency: reads from 总经办 (deepseek) project.
All paths configurable via environment variables.
"""

import os


# ── 总经办 project root ──

DEEPSEEK_PROJECT_ROOT = os.environ.get(
    "DEEPSEEK_PROJECT_ROOT",
    r"C:\Users\Augfoto ASUS\Documents\deepseek",
)

# ── Input: deep_dives directory ──

DEEP_DIVES_DIR = os.environ.get(
    "TEXTBOOK_DEEP_DIVES_DIR",
    r"C:\Users\Augfoto ASUS\Documents\01 内容\CCBrain\deep_dives",
)

# ── Output: where generated Luffa JSON is saved ──

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data", "textbook")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ── LLM config ──

LLM_MODEL = os.environ.get("TEXTBOOK_LLM_MODEL", None)
LLM_MAX_TOKENS = int(os.environ.get("TEXTBOOK_MAX_TOKENS", "16384"))


def validate():
    """Check that the 总经办 project is accessible. Returns (ok, message)."""
    if not os.path.isdir(DEEPSEEK_PROJECT_ROOT):
        return False, f"总经办 project not found: {DEEPSEEK_PROJECT_ROOT}"
    if not os.path.isdir(DEEP_DIVES_DIR):
        return False, f"deep_dives directory not found: {DEEP_DIVES_DIR}\n  (run content_repurpose.py or create manually)"
    return True, "OK"
