"""Test MCP protocol layer end-to-end: initialize, list_tools, call_tool."""

import json
import subprocess
import sys
import os
import asyncio

SERVER_SCRIPT = os.path.join(os.path.dirname(__file__), "..", "servers", "podcast", "server.py")

class MCPClient:
    def __init__(self):
        self.proc = None
        self._msg_id = 0

    async def start(self):
        self.proc = await asyncio.create_subprocess_exec(
            sys.executable, SERVER_SCRIPT,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

    async def send(self, method: str, params: dict = None):
        self._msg_id += 1
        msg = {"jsonrpc": "2.0", "id": self._msg_id, "method": method}
        if params:
            msg["params"] = params
        self.proc.stdin.write((json.dumps(msg) + "\n").encode())
        await self.proc.stdin.drain()
        line = await self.proc.stdout.readline()
        return json.loads(line.decode())

    async def close(self):
        self.proc.terminate()
        await self.proc.wait()


async def main():
    client = MCPClient()
    await client.start()

    # Step 1: Initialize
    print("=== 1. initialize ===")
    resp = await client.send("initialize", {
        "protocolVersion": "2024-11-05",
        "capabilities": {},
        "clientInfo": {"name": "test-host", "version": "0.1.0"},
    })
    init_result = resp.get("result", {})
    print(f"  Server name: {init_result.get('serverInfo', {}).get('name')}")
    print(f"  Server version: {init_result.get('serverInfo', {}).get('version')}")
    print(f"  Protocol: {init_result.get('protocolVersion')}")
    assert init_result["serverInfo"]["name"] == "jiuge-podcast"
    print("  [OK] initialize")

    # Step 2: Send initialized notification (required by protocol)
    notif = {"jsonrpc": "2.0", "method": "notifications/initialized"}
    client.proc.stdin.write((json.dumps(notif) + "\n").encode())
    await client.proc.stdin.drain()

    # Step 3: List tools
    print("\n=== 2. tools/list ===")
    resp = await client.send("tools/list")
    tools = resp.get("result", {}).get("tools", [])
    print(f"  Found {len(tools)} tool(s):")
    for t in tools:
        print(f"    - {t['name']}: {t['description']}")
    assert any(t["name"] == "analyze_podcast" for t in tools)
    print("  [OK] tools/list")

    # Step 4: Call tool (stub, no API key needed for schema)
    print("\n=== 3. tools/call (stub URL) ===")
    resp = await client.send("tools/call", {
        "name": "analyze_podcast",
        "arguments": {"url": "https://www.xiaoyuzhoufm.com/episode/test"},
    })
    content = resp.get("result", {}).get("content", [])
    print(f"  Response: {content[0]['text'][:100]}..." if content else "  No content")
    print("  [OK] tools/call")

    await client.close()
    print("\n[PASS] All protocol checks passed")


if __name__ == "__main__":
    asyncio.run(main())
