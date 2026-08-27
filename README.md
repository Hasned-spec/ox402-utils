# ox402-utils

**87 paid tools for AI agents and humans — payable per call via x402 (USDC on Base).**
Web research, security recon, **neural text-to-speech (Kokoro-82M)**, speech, document + media
conversion, full-page screenshots, AI image/text, resume parsing, and SSL/breach audits.
No accounts, no API keys, no subscription.

> **Live site:** https://deviant-oils-guardian-coating.trycloudflare.com (tunnel rotates — the current URL is always in `docs/api.txt` and `/.well-known/x402`).
> MCP server: **`/mcp402/`** · Catalog: **`/x402/catalog`** · Machine-readable: **`/llms.txt`** · Agent manifest: **`/.well-known/ai-plugin.json`**

---


## Quick Start (Agent SDK)

Copy-paste this into your agent to call any tool via x402 (USDC on Base):

```python
import httpx, os

BASE = os.getenv("OX402_BASE", "https://deviant-oils-guardian-coating.trycloudflare.com/x402")
WALLET = os.getenv("WALLET_ADDRESS")  # 0x... your wallet (optional for free trial)

async def call(tool: str, payload: dict):
    async with httpx.AsyncClient(timeout=30.0) as client:
        r = await client.post(f"{BASE}/trial/{tool}", json=payload)
        if r.status_code == 200:
            return r.json()
        if r.status_code == 402:
            # payment required - pay with x402 facilitator
            pay = r.json()
            # (integrate with x402 facilitator / wallet here)
            raise RuntimeError(f"Paid tool {tool}: {pay['amount']} USDC")
        r.raise_for_status()

# Free trial (10 calls/IP on tier=free tools)
print(await call("search", {"query": "x402 protocol", "count": 5}))
# Paid tool example
# print(await call("stt", {"url": "https://example.com/audio.mp3"}))
```

For production: swap `/trial/` -> `/paid/` and use the x402 facilitator to settle USDC on Base.

## Why this exists

An AI agent's sandbox can't open a browser, run a neural TTS model, scan a host for open ports,
or audit a site's TLS. ox402 does those for it — and bills per call in USDC. No signup, no
API key, no monthly minimum. Every call is authorized by an on-chain micropayment
([x402](https://www.x402.org)): hit the endpoint, get a `402` challenge, pay the exact amount,
retry with the `X-Payment` header.

**Free trial:** the first **5 calls per IP** on tier=`free` tools run free — no wallet, no signup —
via `POST /x402/trial/<tool>`. Paid-tier tools always require an x402 USDC payment.

## Use it in 30 seconds

**Free trial call (no payment):**
```bash
curl -s https://deviant-oils-guardian-coating.trycloudflare.com/x402/trial/search \
  -H 'Content-Type: application/json' \
  -d '{"query":"x402 protocol","count":3}'
```

**Paid call (x402 handshake):**
```bash
curl -i https://deviant-oils-guardian-coating.trycloudflare.com/x402/paid/search \
  -H 'Content-Type: application/json' \
  -d '{"query":"x402 protocol","count":3}'
```
The `402` response carries a `PAYMENT-REQUIRED` challenge with the exact USDC amount and the
`payTo` address. Pay on Base, then repeat the request with the signed payment in the
`X-Payment` header (any x402 client: the Coinbase `x402` fetch wrapper, or your own signer).
Verified via the CDP facilitator; settled on-chain.

## MCP server (Claude / any MCP client)

```json
{
  "mcpServers": {
    "ox402-utils": { "url": "https://deviant-oils-guardian-coating.trycloudflare.com/mcp402/" }
  }
}
```
`tools/list` is free and returns all 76 MCP-exposed tools. `tools/call` returns the payment
instructions when unpaid. Drop it into Claude Desktop, Cursor, or any MCP framework and the
agent can pay-to-use every tool.

## What's inside (88 tools)

| group | examples |
|-------|----------|
| Research & web | `search`, `html2md`, `web-scrape`, `extract-structured`, `deep-search`, `research-brief`, `citations`, `fact-check`, `web-archive` |
| Documents & media | `pdf-extract`, `ocr`, `md2pdf`, `pdf-invoice`, `video-download`, `video2mp3`, `image-optimize`, `image-compress`, `capture-page` (full-page screenshot/PDF), `screenshot-mobile`, `pdf-merge` |
| Speech | `stt` / `stt-fast` (Whisper), `tts` (**neural Kokoro-82M**, 30+ voices, $0.004/1k chars), `tts-voices` |
| Security & recon | `security-headers`, `cors-check`, `cookie-flags`, `dns-recon`, `port-scan`, `leak-check`, `subdomain-find`, `threat-intel`, `site-report`, `file-scan`, `email-verify`, `reverse-dns`, `header-compare` |
| AI (paid) | `ai-image`, `ai-rewrite`, `ai-summarize`, `ai-text`, `translate`, `resume-parse`, `pdf-to-word`, `plagiarism`, `qr`, `link-preview`, `pdf-compress`, `video-thumb` |
| Finance & world | `crypto-price`, `stock-quote`, `fx-rates`, `weather`, `geoip` |
| Dev & data | `http-headers`, `ssl-check`, `exec-python`, `repo2context`, `md-compress`, `temp-webhook`, `robots`, `sitemap`, `link-health` |

## Pricing (buyer-friendly, per call)

- Most tools **$0.001–$0.01**.
- Speech & video **bill per started minute** — `stt` $0.006/min, `stt-fast` $0.002/min,
  `video2mp3` / `video-download` ~$0.0004/min of source (no file-size cap).
- Neural TTS `tts` $0.004 per 1k chars.
- Range across all 88: **$0.001 to $0.10**.
- **First 5 calls/IP free** on tier=`free` tools (via `/x402/trial/`).

Full catalog with live prices: **`/x402/catalog`** (rendered on the live site).

## Safety & isolation (for you and for us)

- **Browser captures run in a fresh, throwaway Chromium profile every call** — no saved
  logins, cookies, or extensions persist, and the renderer is blocked from private/loopback
  addresses (127.0.0.1, 10.x, 192.168.x, …). It can only fetch the public URL you give it.
- **Uploads are never executed.** `file-scan`, `strip-metadata`, and image tools parse your
  bytes in memory and return a result; inputs are not retained after the call.
- Everything runs **on-CPU** (no NVIDIA/cloud generative models) — no upstream outages.

## Discovery

- Agent-readable: **`/.well-known/x402`** (full endpoint manifest), **`/.well-known/ai-plugin.json`** (tool schemas), and **`/llms.txt`**.
- Listed on the **402index** x402 service registry.
- MCP server at **`/mcp402/`** (streamable HTTP).

---

*Pay-to address `0x7869d1fe2d1de863b6fae4594d392343a69ed8e3` · Base mainnet USDC.*
