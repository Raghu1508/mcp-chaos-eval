#!/usr/bin/env python3
"""mcp-chaos-eval, day 1: a stdio proxy that corrupts MCP tool-call responses.

Sits between an MCP client and a real MCP server. Every JSON-RPC response to a
`tools/call` request gets its JSON truncated mid-payload, so you can watch how
the client/agent copes with a malformed tool result.

Usage (point your MCP client at this instead of the real server):
    python3 chaos_proxy.py -- npx -y @modelcontextprotocol/server-filesystem /tmp
"""
import json
import subprocess
import sys
import threading

LOG = open("chaos.log", "a", buffering=1)
tool_call_ids = set()


def log(direction, line):
    LOG.write(f"{direction} {line.rstrip()}\n")


def client_to_server(server):
    for line in sys.stdin:
        try:
            msg = json.loads(line)
            if msg.get("method") == "tools/call":
                tool_call_ids.add(msg.get("id"))
        except json.JSONDecodeError:
            pass
        log(">>", line)
        server.stdin.write(line)
        server.stdin.flush()
    server.stdin.close()


def corrupt(line):
    # Fault: malformed JSON. Cut the payload in half and drop the newline-safe tail.
    body = line.rstrip("\n")
    return body[: len(body) // 2] + '",}\n'


def main():
    cmd = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else sys.argv[1:]
    if not cmd:
        sys.exit("usage: chaos_proxy.py -- <mcp server command>")
    server = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
    threading.Thread(target=client_to_server, args=(server,), daemon=True).start()

    for line in server.stdout:
        try:
            msg_id = json.loads(line).get("id")
        except json.JSONDecodeError:
            msg_id = None
        if msg_id is not None and msg_id in tool_call_ids:
            line = corrupt(line)
            log("!! CORRUPTED", line)
        else:
            log("<<", line)
        sys.stdout.write(line)
        sys.stdout.flush()


if __name__ == "__main__":
    main()
