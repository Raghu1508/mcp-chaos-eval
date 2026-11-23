# mcp-chaos-eval

Adversarial chaos testing for MCP servers.

Day 1: `chaos_proxy.py` wraps any stdio MCP server and corrupts every `tools/call` response (malformed JSON).

```bash
python3 chaos_proxy.py -- npx -y @modelcontextprotocol/server-filesystem /tmp
```

Traffic is logged to `chaos.log`.
