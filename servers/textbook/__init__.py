"""Textbook MCP server — generate interactive Luffa SuperBox content from deep_dives."""

import json
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.types import ServerCapabilities, Tool, TextContent

from servers.textbook.generator import generate_interactive, list_topics
from servers.textbook.luffa_bridge import pack_to_superbox, export_superbox
from servers.textbook.config import validate as config_validate

server = Server("jiuge-textbook")

_INPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "topic": {
            "type": "string",
            "description": "Topic name (deep_dives filename without .md suffix). Use 'list' to see available topics.",
        },
        "module_types": {
            "type": "string",
            "description": "Comma-separated module types: simulator,quiz,comparison. Default: all three.",
            "default": "",
        },
        "lang": {
            "type": "string",
            "description": "Output language: 'zh' (Chinese, default) or 'en' (English)",
            "default": "",
        },
    },
    "required": ["topic"],
}


@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="generate_interactive",
            description="Generate interactive Luffa SuperBox content from deep_dives analysis. "
            "Reads a CCBrain/deep_dives/*.md file, uses LLM to extract key concepts, "
            "and produces simulator/quiz/comparison modules in Luffa JSON format.",
            inputSchema=_INPUT_SCHEMA,
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    if name != "generate_interactive":
        raise ValueError(f"Unknown tool: {name}")

    topic = arguments.get("topic", arguments.get("topic", ""))
    module_types_raw = arguments.get("module_types", "")
    lang = arguments.get("lang", "")

    if lang == "en":
        content_lang = "en"
    else:
        content_lang = "zh"

    if topic == "list":
        topics = list_topics()
        if not topics:
            text = "[Textbook] No deep_dives found. Run content_repurpose.py in 总经办 first."
        else:
            text = f"[Textbook] Available topics ({len(topics)}):\n" + "\n".join(f"  - {t}" for t in topics)
        return [TextContent(type="text", text=text)]

    module_types = None
    if module_types_raw:
        module_types = [t.strip() for t in module_types_raw.split(",") if t.strip()]

    valid, msg = config_validate()
    if not valid:
        return [TextContent(type="text", text=f"[Textbook] Config error: {msg}")]

    try:
        result = generate_interactive(topic, module_types=module_types)
    except FileNotFoundError as e:
        return [TextContent(type="text", text=f"[Textbook] Topic not found: {e}")]
    except Exception as e:
        return [TextContent(type="text", text=f"[Textbook] Generation failed: {e}")]

    metadata = {
        "id": result.get("topicId", topic),
        "title": result.get("topicTitle", topic),
        "description": result.get("topicDescription", ""),
    }

    superbox = pack_to_superbox(
        topic=result.get("topicTitle", topic),
        modules=result.get("modules", []),
        metadata=metadata,
    )

    filepath = export_superbox(superbox)

    module_count = len(superbox.get("modules", []))
    module_summary = ", ".join(
        f"{m['type']}({m.get('title', '')})" for m in superbox.get("modules", [])
    )

    text = f"""[Textbook] Generated Luffa SuperBox for: {result.get('topicTitle', topic)}
Modules: {module_count} ({module_summary})
Saved to: {filepath}"""

    return [TextContent(type="text", text=text)]


async def run():
    from mcp.server.stdio import stdio_server
    async with stdio_server() as (read, write):
        await server.run(
            read,
            write,
            InitializationOptions(
                server_name="jiuge-textbook",
                server_version="0.1.0",
                capabilities=ServerCapabilities(),
            ),
        )


if __name__ == "__main__":
    import asyncio
    asyncio.run(run())
