"""LLM caller — auto-detects provider from environment."""

from openai import OpenAI
from core.config import detect_provider, MAX_TOKENS_DEFAULT, MAX_TOKENS_REPORT

_client = None
_provider = None

def _get_provider():
    global _provider
    if _provider is None:
        _provider = detect_provider()
    return _provider

def get_client():
    global _client
    if _client is None:
        cfg = _get_provider()
        _client = OpenAI(api_key=cfg["api_key"], base_url=cfg["base_url"])
    return _client

def default_model() -> str:
    return _get_provider()["default_model"]

def call_llm(system_prompt, user_prompt, model=None, max_tokens=MAX_TOKENS_DEFAULT, temperature=0.3):
    client = get_client()
    resp = client.chat.completions.create(
        model=model or default_model(),
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        max_tokens=max_tokens,
        temperature=temperature,
    )
    return resp.choices[0].message.content

def call_llm_report(system_prompt, user_prompt, model=None):
    return call_llm(system_prompt, user_prompt, model=model, max_tokens=MAX_TOKENS_REPORT, temperature=0.3)
