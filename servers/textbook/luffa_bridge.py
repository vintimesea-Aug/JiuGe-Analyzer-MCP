"""Luffa SuperBox bridge — pack interactive modules into Luffa JSON schema.

Schema reference:
  Luffa SuperBox expects:
  - id, title, description (metadata)
  - modules[] — interactive content blocks
    - simulator: interactive parameter explorer
    - quiz: multiple-choice questions with feedback
    - comparison: side-by-side comparisons
  - dataSources[] — realtime data feeds (optional)
  - createdAt, version
"""

import json
import os
import datetime

from servers.textbook.config import OUTPUT_DIR


def _make_module_simulator(item: dict) -> dict:
    return {
        "type": "simulator",
        "id": item.get("id", ""),
        "title": item.get("title", ""),
        "description": item.get("description", ""),
        "parameters": item.get("parameters", []),
        "formula": item.get("formula", ""),
        "chartConfig": item.get("chartConfig", {}),
        "explanation": item.get("explanation", ""),
    }


def _make_module_quiz(item: dict) -> dict:
    return {
        "type": "quiz",
        "id": item.get("id", ""),
        "title": item.get("title", ""),
        "questions": [
            {
                "id": q.get("id", f"q{i}"),
                "text": q.get("text", q.get("question", "")),
                "options": q.get("options", []),
                "correctIndex": q.get("correctIndex", q.get("correct_index", 0)),
                "explanation": q.get("explanation", ""),
            }
            for i, q in enumerate(item.get("questions", []))
        ],
    }


def _make_module_comparison(item: dict) -> dict:
    return {
        "type": "comparison",
        "id": item.get("id", ""),
        "title": item.get("title", ""),
        "left": item.get("left", {}),
        "right": item.get("right", {}),
        "dimensions": item.get("dimensions", []),
    }


_MODULE_BUILDERS = {
    "simulator": _make_module_simulator,
    "quiz": _make_module_quiz,
    "comparison": _make_module_comparison,
}


def pack_to_superbox(topic: str, modules: list[dict], metadata: dict | None = None) -> dict:
    """Convert generator output to Luffa SuperBox JSON structure."""
    packaged_modules = []
    for m in modules:
        mtype = m.get("type", "")
        builder = _MODULE_BUILDERS.get(mtype)
        if builder:
            packaged_modules.append(builder(m))
        else:
            packaged_modules.append(m)

    meta = metadata or {}
    now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    return {
        "id": meta.get("id", topic.lower().replace(" ", "_")),
        "title": meta.get("title", topic),
        "description": meta.get("description", ""),
        "sourceUrl": meta.get("sourceUrl", ""),
        "sourceDate": meta.get("sourceDate", ""),
        "modules": packaged_modules,
        "dataSources": meta.get("dataSources", []),
        "createdAt": now,
        "version": "1.0",
    }


def export_superbox(box: dict, filename: str | None = None) -> str:
    """Write SuperBox JSON to file. Returns file path."""
    if filename is None:
        filename = f"{box['id']}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    filepath = os.path.join(OUTPUT_DIR, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(box, f, ensure_ascii=False, indent=2)
    return filepath
