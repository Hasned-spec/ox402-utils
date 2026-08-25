# ox402-utils

**49 micro-priced utilities for AI agents.** Web search, whois, DNS, geo-IP, crypto/stock/FX
prices, weather, OCR, screenshots, PDF invoices, video download links, ephemeral agent memory,
scraping, CSV/JSON conversion and more.
No accounts, no API keys — every call is authorized by an on-chain micropayment
(**x402**: USDC on Base, $0.003–$0.05 per call).

## Use it in 30 seconds (curl)

**Free tier: your first 5 calls are free (lifetime, per network) — no wallet, no signup.**
After that, per-call x402.


```bash
# any tool: POST JSON -> 402 challenge -> pay -> retry with X-Payment header
curl -i https://organisation-anticipated-objects-restrictions.trycloudflare.com/x402/paid/search \
  -H 'Content-Type: application/json' \
  -d '{"query":"x402 protocol","count":3}'
```

The `402` response carries a `PAYMENT-REQUIRED` base64 challenge with everything a wallet needs:

```
{"accepts":[{"scheme":"exact","network":"eip155:8453","maxAmountRequired":"0.008",
  "payTo":"0x7869d1fe2d1de863b6fae4594d392343a69ed8e3",
  "asset":"0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"}...]}
```

Pay the exact USDC amount on Base, then repeat the request with the signed payment in the
`X-Payment` header (any x402 client does this: the Coinbase `x402` fetch wrapper,
`lnget`-style flows, or your own signer). Verified via the CDP facilitator; settled on-chain.

## MCP server (Claude / any MCP client)

```json
{
  "mcpServers": {
    "ox402-utils": {
      "url": "https://organisation-anticipated-objects-restrictions.trycloudflare.com/mcp402/"
    }
  }
}
```

`tools/list` is free and shows all 45 tools with per-call prices baked into descriptions.
`tools/call` returns the payment instructions when unpaid.

## Python client (+ LangChain adapter)

See [`sdk/ox402_client.py`](sdk/ox402_client.py):

```python
from ox402_client import ox402

ox402.pay = my_payer   # callable(challenge: dict) -> "X-Payment" header value
result = ox402.call('whois', {'domain': 'github.com'})

# LangChain:
tools = ox402.langchain_tools(pay=my_payer, names={'search', 'screenshot', 'pdf-invoice'})
```

## Catalog highlights

| tool | price | what you get |
|------|------:|--------------|
| video-info | $0.006 | metadata + all formats for YouTube/TikTok/Vimeo/X/1000+ sites |
| video-download | $0.015 | direct download links for any video URL |
| search | $0.008 | web results (title/url/snippet) |
| screenshot | $0.015 | headless-chrome PNG of any URL |
| pdf-invoice | $0.02 | invoice/receipt PDF w/ items+tax |
| ocr | $0.02 | image → text (tesseract) |
| html2md | $0.006 | page → clean markdown + links |
| whois | $0.01 | registrar/dates/NS/availability |
| geoip | $0.004 | country/city/ISP/proxy flags |
| stock-quote | $0.004 | last price + prev close |
| crypto-price | $0.003 | spot + 24h change |
| weather | $0.003 | current + 3-day forecast |

Free catalog endpoint: `GET https://organisation-anticipated-objects-restrictions.trycloudflare.com/x402/`
(45 tools with prices + example payloads).

Also indexed on [402index.io](https://402index.io) as `ox402-*` services.

## Notes

- Endpoint is a Cloudflare quick tunnel; if it rotates, the catalog at `/x402/` always shows
  the live host. Permanent domain pending (is-a.dev PR open).
- Seller wallet: `0x7869d1fe2d1de863b6fae4594d392343a69ed8e3` (Base).

## Wire it into any agent in 10 seconds

Paste into a system prompt (Claude, GPT, OpenCode, whatever you run):

```
You can call paid utility APIs via x402 (USDC on Base).
Catalog: GET https://organisation-anticipated-objects-restrictions.trycloudflare.com/x402
Call pattern: POST https://organisation-anticipated-objects-restrictions.trycloudflare.com/x402/paid/<tool>
  with JSON body -> if 402 with PAYMENT-REQUIRED header, sign+pay the USDC request,
  retry once with X-Payment header. Prices $0.001-$0.05/call.
First 5 calls from your network are free - probe before paying.
Prefer kv-put/kv-get for cross-run state; screenshot/html2md for page capture;
video-download for media links; pdf-extract/ocr for documents.
Budget cap: $0.10/day unless I say otherwise.
```

MCP clients: add `"ox402": {"url": "https://organisation-anticipated-objects-restrictions.trycloudflare.com/mcp402/"}`.

## Tool catalog

| tool | price | what it does |
|---|---|---|
| `kv-get` | $0.001 | Read a key from ox402 ephemeral memory (written via kv-put). Returns found/value/ttl_seconds_left. Read-only. |
| `kv-put` | $0.002 | Store a JSON value in ephemeral shared memory for stateless agents. TTL 1-24h, value <= 8KB, namespaced keys. Mutating. |
| `crypto-price` | $0.003 | Crypto spot prices + 24h change (CoinGecko ids) |
| `fx-rates` | $0.003 | Fiat FX rates (ECB daily) |
| `weather` | $0.003 | Current weather + 3-day forecast by city/coords |
| `geoip` | $0.004 | IP geolocation: country/city/ISP/proxy/hosting flags |
| `stock-quote` | $0.004 | Stock quote: last price, prev close, exchange (Yahoo) |
| `hash` | $0.005 | SHA-256/512/any hash of payload |
| `base64` | $0.005 | base64 encode/decode |
| `uuid` | $0.005 | Generate UUID v4 |
| `jwt-decode` | $0.005 | Decode JWT (no verify) |
| `url-encode` | $0.005 | URL encode/decode |
| `regex-extract` | $0.005 | Regex match extraction |
| `csv2json` | $0.005 | CSV to JSON array |
| `json-format` | $0.005 | Pretty/minify JSON |
| `yaml2json` | $0.005 | YAML to JSON |
| `timestamp` | $0.005 | Unix<->ISO timestamp |
| `diff` | $0.005 | Unified line diff |
| `html2text` | $0.005 | Strip HTML to text |
| `qrcode` | $0.005 | QR code as PNG data-url |
| `password` | $0.005 | Random password |
| `json-merge` | $0.005 | Deep-merge two JSON |
| `csv-sum` | $0.005 | Sum a CSV column |
| `unit-convert` | $0.005 | Unit convert (len/mass/temp) |
| `json2csv` | $0.005 | JSON array to CSV |
| `schema-validate` | $0.005 | Validate JSON vs schema |
| `json-pointer` | $0.005 | Extract by JSON path |
| `csv-col` | $0.005 | Extract CSV column |
| `text-replace` | $0.005 | Find/replace in text |
| `sort-json` | $0.005 | Sort JSON array by key |
| `unique` | $0.005 | Unique lines/values |
| `wayback` | $0.005 | Wayback Machine snapshot + optional history |
| `dns-lookup` | $0.006 | DNS records: A/AAAA/MX/NS/TXT/CNAME |
| `html2md` | $0.006 | HTML page/page-url -> clean markdown + links |
| `video-info` | $0.006 | Video metadata + all formats (YouTube, TikTok, Vimeo, X, SoundCloud, 1000+ sites) |
| `search` | $0.008 | Web search (DDG): title+url+snippet per result |
| `whois` | $0.010 | Domain WHOIS: registrar, dates, nameservers, availability |
| `text2img` | $0.010 | Render text to PNG image (dark/light) |
| `pdf-text` | $0.010 | Plain text to formatted PDF document |
| `screenshot` | $0.015 | Headless-chrome screenshot PNG of any URL |
| `video-download` | $0.015 | Direct download links for a video URL (yt-dlp, 1000+ platforms) |
| `web-scrape` | $0.020 | Server-side URL scrape (title+text) |
| `youtube-info` | $0.020 | YouTube metadata + streams |
| `base64-url` | $0.020 | Fetch URL -> base64 (capped 25MB) |
| `ocr` | $0.020 | OCR image to text (tesseract, url or base64) |
| `pdf-invoice` | $0.020 | Generate invoice/receipt PDF (items, tax, logo) |
| `pdf-extract` | $0.030 | Extract text from PDF |
| `image-resize` | $0.030 | Resize/convert image |
| `youtube-dl` | $0.050 | YouTube download (mp3/mp4, capped 25MB) |
