"""MCP server helpers — protocol-level utilities shared across servers."""

import json
from typing import Any

from .security import scan_tools

def make_tool_result(content: str, is_error: bool = False) -> dict:
    return {
        "content": [{"type": "text", "text": content}],
        "isError": is_error,
    }

def make_resource_result(uri: str, text: str, mime_type: str = "text/markdown") -> dict:
    return {
        "uri": uri,
        "mimeType": mime_type,
        "text": text,
    }

def audit_tools(tools: list[dict]) -> dict:
    """审计 tool 列表的安全性，返回 {pass, warnings, errors}"""
    return scan_tools(tools)
