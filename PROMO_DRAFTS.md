# ox402-utils — promo drafts (paste where noted; no auth from VM)

STABLE MCP ENDPOINT (primary, never rotates):
  http://129.213.128.185/mcp402/
HTTP API (stable IP):
  http://129.213.128.185/x402/catalog
  http://129.213.128.185/x402/trial/<tool>  (free 10/IP)
  http://129.213.128.185/x402/paid/<tool>   (x402 USDC)
Landing: https://hasned-spec.github.io/ox402-utils/
GitHub: https://github.com/Hasned-spec/ox402-utils

NOTE: The tunnel host rotates; the IP above is permanent. Use the IP.

=====================================================================
SHOW HN
=====================================================================
Title: Show HN: ox402 – 94 utility APIs for AI agents, paid per call via x402 (USDC on Base)

Body:
ox402 is a self-serve utility grid for AI agents (and humans). 94 tools across
web research, PDF/OCR, neural TTS (Kokoro), Whisper STT, security recon, dev
utilities, media conversion, SQL sandbox, embeddings, GraphQL/OpenAPI introspection.
Every call settles in USDC on Base via the x402 protocol — no API key, no account.

Free tier: 10 calls/IP. MCP server (streamable HTTP) at the stable endpoint so any
MCP client gets all 94 tools and pays automatically:

  http://129.213.128.185/mcp402/

(HTTP, not HTTPS — the VM's port 443 is firewalled; agents using MCP-over-HTTP
connect fine. Payments verified+settled via our self-hosted facilitator.)

Catalog: http://129.213.128.185/x402/catalog
Landing: https://hasned-spec.github.io/ox402-utils/

Honest status: $0 revenue so far (just launched, fixing discovery), but the payment
path is verified end-to-end. AMA.

=====================================================================
REDDIT  r/ethfinance / r/AI_Agents / r/ethereum
=====================================================================
Title: Built ox402 — 94 agent utility APIs you pay for per-call in USDC (x402 on Base)

Body:
Shipping a real, working x402 service for AI agents. 94 micro-utilities
(research, PDF/OCR, neural TTS, speech-to-text, security recon, dev tools,
media, SQL, embeddings) that any agent can call and pay for in USDC on Base —
no signup, no API keys. Free trial: 10 calls/IP.

MCP server at stable endpoint (connect any MCP client):
  http://129.213.128.185/mcp402/

We self-host the facilitator so settlement actually works without Coinbase CDP
keys. Try it: https://hasned-spec.github.io/ox402-utils/

=====================================================================
X / TWITTER
=====================================================================
1/ Launched ox402 — 94 utility APIs for AI agents that pay per call in USDC via
@x402_ standard on Base. No keys, no accounts. MCP at stable IP:
http://129.213.128.185/mcp402/

2/ Tools: web research, PDF+OCR, Kokoro neural TTS, Whisper STT, security recon,
dev utilities, media conversion, SQL sandbox, embeddings, GraphQL/OpenAPI.
Agents just call and pay via x402.

3/ MCP server for any MCP client (Claude, Cursor, LangChain) gets all 94 tools and
pays automatically. Self-hosted facilitator, no CDP key needed.
Catalog: http://129.213.128.185/x402/catalog

=====================================================================
MCP CLIENT SNIPPET (for agents/humans)
=====================================================================
{
  "mcpServers": {
    "ox402-utils": { "url": "http://129.213.128.185/mcp402/" }
  }
}
