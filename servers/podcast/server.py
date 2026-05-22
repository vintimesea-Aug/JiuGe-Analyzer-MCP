"""Podcast MCP server — analyze Xiaoyuzhou podcast episodes."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.types import ServerCapabilities, Tool, TextContent
from servers.podcast.pipeline import analyze_episode, analyze_episode_deep

server = Server("jiuge-podcast")

_URL_SCHEMA = {
    "type": "object",
    "properties": {
        "url": {
            "type": "string",
            "description": "Xiaoyuzhou episode URL (e.g. https://www.xiaoyuzhoufm.com/episode/...)",
        },
        "lang": {
            "type": "string",
            "description": "Output language: 'zh' (Chinese, default) or 'en' (English)",
            "default": "",
        },
    },
    "required": ["url"],
}

@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="analyze_podcast",
            description="Quick analysis of a Xiaoyuzhou podcast episode by URL (metadata only, ~30s)",
            inputSchema=_URL_SCHEMA,
        ),
        Tool(
            name="analyze_podcast_deep",
            description="Deep analysis with transcript (downloads audio + Whisper, ~2-5min). Use for full depth.",
            inputSchema=_URL_SCHEMA,
        ),
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    url = arguments["url"]
    lang = arguments.get("lang", "")
    if name == "analyze_podcast":
        result = analyze_episode(url, lang)
    elif name == "analyze_podcast_deep":
        result = analyze_episode_deep(url, lang)
    else:
        raise ValueError(f"Unknown tool: {name}")

    text = f"""{result['summary']}
[File] {result['file']}
[Tip] 设置环境变量 JIUGE_OUTPUT_DIR 可自定义输出目录"""
    return [TextContent(type="text", text=text)]

async def run():
    from mcp.server.stdio import stdio_server
    async with stdio_server() as (read, write):
        await server.run(
            read, write,
            InitializationOptions(
                server_name="jiuge-podcast",
                server_version="0.1.0",
                capabilities=ServerCapabilities(),
            ),
        )

if __name__ == "__main__":
    import asyncio
    asyncio.run(run())
