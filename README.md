# ox402-utils

**94 capability APIs an AI agent can't run in its own sandbox — paid per call via x402 (USDC on Base).**
Web research, security recon, **neural text-to-speech (Kokoro-82M)**, speech, document + media
conversion, full-page screenshots, SSL/breach audits, SQL sandboxes, embeddings, and more.
No accounts, no API keys, no subscription. **Free trial: 10 calls/IP on tier=free tools.**

[![Hasned-spec/ox402-utils MCP server](https://glama.ai/mcp/servers/Hasned-spec/ox402-utils/badges/score.svg)](https://glama.ai/mcp/servers/Hasned-spec/ox402-utils)

> Live site: **the current tunnel URL is published in `api.txt` and `/.well-known/x402` on this repo's served docs, and rotates periodically — fetch `api.txt` for the live endpoint.**
> MCP server: **`/mcp402/`** · Catalog: **`/x402/catalog`** · Machine-readable: **`/llms.txt`**

---

## Why this exists

An AI agent's sandbox can't open a browser, run a GPU TTS model, scan a host for open ports,
or audit a site's TLS. ox402 does those for it — and bills per call in USDC. No signup, no
API key, no monthly minimum. Every call is authorized by an on-chain micropayment
([x402](https://www.x402.org)): hit the endpoint, get a `402` challenge, pay the exact amount,
retry with the `X-Payment` header.

**Free trial: 10 calls/IP on tier=free tools.** Paid-tier tools always require x402 USDC.

## Use it in 30 seconds (curl)

```bash
# Free trial (10 calls/IP): no payment needed
curl -X POST https://deviant-oils-guardian-coating.trycloudflare.com/x402/trial/search \
  -H 'Content-Type: application/json' \
  -d '{"query":"x402 protocol","count":3}'

# Paid tier: POST -> 402 challenge -> pay -> retry with X-Payment header
curl -i https://deviant-oils-guardian-coating.trycloudflare.com/x402/paid/search \
  -H 'Content-Type: application/json' \
  -d '{"query":"x402 protocol","count":3}'
```

The `402` response carries a `PAYMENT-REQUIRED` challenge with the exact USDC amount and the
`payTo` address. Pay on Base, then repeat the request with the signed payment in the
`X-Payment` header (any x402 client: the Coinbase `x402` fetch wrapper, or your own signer).
Verified + settled via our self-hosted facilitator (melonask/facilitator) on Base mainnet.

## MCP server (Claude / any MCP client)

```json
{
  "mcpServers": {
    "ox402-utils": { "url": "https://deviant-oils-guardian-coating.trycloudflare.com/mcp402/" }
  }
}
```

`tools/list` is free and returns all 94 tools (compact ~1.6k-token menu; full schemas on
demand). `tools/call` returns the payment instructions when unpaid. Drop it into Claude
Desktop, Cursor, or any MCP framework and the agent can pay-to-use every tool.

## What's inside (94 tools)

| group | examples |
|-------|----------|
| Research & web | `search`, `html2md`, `web-scrape`, `extract-structured`, `deep-search`, `research-brief`, `citations`, `fact-check`, `web-archive`, `openapi-fetch`, `graphql` |
| Documents & media | `pdf-extract`, `ocr`, `md2pdf`, `pdf-invoice`, `video-download`, `video2mp3`, `image-optimize`, `image-compress`, `capture-page` (full-page screenshot/PDF), `screenshot-mobile`, `pdf-merge`, `pdf-compress` |
| Speech | `stt` / `stt-fast` (Whisper), `tts` (**neural Kokoro-82M**, 30+ voices, $0.004/1k chars), `tts-voices` |
| Security & recon | `security-headers`, `cors-check`, `cookie-flags`, `dns-recon`, `port-scan`, `leak-check`, `subdomain-find`, `threat-intel`, `site-report`, `file-scan`, `email-verify`, `reverse-dns`, `header-compare` |
| Finance & world | `crypto-price`, `stock-quote`, `fx-rates`, `weather`, `geoip` |
| Dev & data | `http-headers`, `ssl-check`, `exec-python`, `repo2context`, `md-compress`, `temp-webhook`, `robots`, `sitemap`, `link-health`, `sqlite`, `embed`, `price-estimate`, `dry-run`, `batch` |
| AI & text | `ai-text`, `ai-rewrite`, `ai-summarize`, `translate`, `resume-parse`, `pdf-to-word`, `plagiarism`, `qr`, `link-preview` |

## Pricing

- **Free tier:** 10 calls/IP on all tier=free tools via `/x402/trial/<tool>` (no wallet, no signup)
- **Paid tier:** $0.001 – $0.10 per call (avg $0.014), USDC on Base mainnet (chain 8453)
- **Payee:** `0xE9C9cC258f7137fD0AbA4Ae513F0Cfa288c0cDc9`

## Self-host

```bash
git clone https://github.com/Hasned-spec/ox402-utils
cd ox402-utils
pip install -r requirements.txt
python3 x402_server.py   # :8793
```

Docker:

```bash
docker build -t ox402 .
docker run -p 8793:8793 -p 8796:8796 ox402
```

## Discovery

- **GitHub Pages:** https://hasned-spec.github.io/ox402-utils/
- **402index:** https://402index.io (search "ox402")
- **Glama:** https://glama.ai/mcp/servers/Hasned-spec/ox402-utils
- **MCP:** `/mcp402/` on the live tunnel

## License

MIT
