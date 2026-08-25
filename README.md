# ox402-utils

**45 micro-priced utilities for AI agents.** Web search, whois, DNS, geo-IP, crypto/stock/FX
prices, weather, OCR, screenshots, PDF invoices, scraping, CSV/JSON conversion and more.
No accounts, no API keys — every call is authorized by an on-chain micropayment
(**x402**: USDC on Base, $0.003–$0.05 per call).

## Use it in 30 seconds (curl)

```bash
# any tool: POST JSON -> 402 challenge -> pay -> retry with X-Payment header
curl -i https://tracy-collar-preview-demands.trycloudflare.com/x402/paid/search \
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
      "url": "https://tracy-collar-preview-demands.trycloudflare.com/mcp402/"
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

Free catalog endpoint: `GET https://tracy-collar-preview-demands.trycloudflare.com/x402/`
(45 tools with prices + example payloads).

Also indexed on [402index.io](https://402index.io) as `ox402-*` services.

## Notes

- Endpoint is a Cloudflare quick tunnel; if it rotates, the catalog at `/x402/` always shows
  the live host. Permanent domain pending (is-a.dev PR open).
- Seller wallet: `0x7869d1fe2d1de863b6fae4594d392343a69ed8e3` (Base).
