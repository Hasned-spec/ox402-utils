# ox402-utils

**57 capability APIs an AI agent can't run in its own sandbox — paid per call via x402 (USDC on Base).**
Web research, security recon, **neural text-to-speech (Kokoro-82M)**, speech, document + media
conversion, full-page screenshots, and SSL/breach audits. No accounts, no API keys, no subscription.

> Live site: **the current tunnel URL is published in `api.txt` and `/.well-known/x402` on this repo's served docs, and rotates periodically — fetch `api.txt` for the live endpoint.**
> MCP server: **`/mcp402/`** · Catalog: **`/x402/catalog`** · Machine-readable: **`/llms.txt`**

---

## Why this exists

An AI agent's sandbox can't open a browser, run a GPU TTS model, scan a host for open ports,
or audit a site's TLS. ox402 does those for it — and bills per call in USDC. No signup, no
API key, no monthly minimum. Every call is authorized by an on-chain micropayment
([x402](https://www.x402.org)): hit the endpoint, get a `402` challenge, pay the exact amount,
retry with the `X-Payment` header.

**There is no free trial.** Every call requires payment — this keeps pricing honest and the
service abuse-free.

## Use it in 30 seconds (curl)

```bash
# Any tool: POST JSON -> 402 challenge -> pay -> retry with X-Payment header
curl -i $(curl -s https://raw.githubusercontent.com/Hasned-spec/ox402-utils/main/docs/api.txt)/x402/paid/search \
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
    "ox402-utils": { "url": "$(curl -s https://raw.githubusercontent.com/Hasned-spec/ox402-utils/main/docs/api.txt)/mcp402/" }
  }
}
```

`tools/list` is free and returns all 57 tools (compact ~1.6k-token menu; full schemas on
demand). `tools/call` returns the payment instructions when unpaid. Drop it into Claude
Desktop, Cursor, or any MCP framework and the agent can pay-to-use every tool.

## What's inside (57 tools)

| group | examples |
|-------|----------|
| Research & web | `search`, `html2md`, `web-scrape`, `extract-structured`, `deep-search`, `research-brief`, `citations`, `fact-check`, `web-archive` |
| Documents & media | `pdf-extract`, `ocr`, `md2pdf`, `pdf-invoice`, `video-download`, `video2mp3`, `image-optimize`, `image-compress`, `capture-page` (full-page screenshot/PDF), `screenshot-mobile`, `pdf-merge` |
| Speech | `stt` / `stt-fast` (Whisper), `tts` (**neural Kokoro-82M**, 30+ voices, $0.004/1k chars), `tts-voices` |
| Security & recon | `security-headers`, `cors-check`, `cookie-flags`, `dns-recon`, `port-scan`, `leak-check`, `subdomain-find`, `threat-intel`, `site-report`, `file-scan`, `email-verify`, `reverse-dns`, `header-compare` |
| Finance & world | `crypto-price`, `stock-quote`, `fx-rates`, `weather`, `geoip` |
| Dev & data | `http-headers`, `ssl-check`, `exec-python`, `repo2context`, `md-compress`, `temp-webhook`, `robots`, `sitemap`, `link-health` |

## Pricing (buyer-friendly, per call)

- Most tools **$0.001–$0.01**.
- Speech & video **bill per started minute** — `stt` $0.006/min, `stt-fast` $0.002/min,
  `video2mp3` / `video-download` ~$0.0004/min of source (no file-size cap).
- Neural TTS `tts` $0.004 per 1k chars.
- Range across all 57: **$0.001 to $0.10**.

Full catalog with live prices: **`/x402/catalog`** (rendered on the live site).

## Safety & isolation (for you and for us)

- **Browser captures run in a fresh, throwaway Chromium profile every call** — no saved
  logins, cookies, or extensions persist, and the renderer is blocked from private/loopback
  addresses (127.0.0.1, 10.x, 192.168.x, …). It can only fetch the public URL you give it.
- **Uploads are never executed.** `file-scan`, `strip-metadata`, and image tools parse your
  bytes in memory and return a result; inputs are not retained after the call.
- Everything runs **on-CPU** (no NVIDIA/cloud generative models) — no upstream outages.

## Discovery

- Agent-readable: **`/.well-known/x402`** (full endpoint manifest) and **`/llms.txt`**.
- Listed on the **402index** x402 service registry.

---

*Pay-to address `0x7869d1fe2d1de863b6fae4594d392343a69ed8e3` · Base mainnet USDC.*
