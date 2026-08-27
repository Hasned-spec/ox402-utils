# ox402-utils — Aggressive Acquisition Posts

## 1. x402 Discord (#x402 channel) — discord.gg/x402
**Title**: ox402-utils — 57 paid tools for agents (MCP + x402), first call $0.004

**Body**:
Hey x402 builders — just launched **ox402-utils**: a self-serve utility grid of **57 paid tools** an AI agent can't run in its own sandbox, all payable per-call via x402 (USDC on Base).

**What's inside:**
- 🔬 **Research**: web search, deep research briefs, repo→context, crypto prices
- 🛡️ **Security**: SSL/TLS audits, header analysis, cookie flags, DNS recon, subdomain find, threat intel, breach checks
- 📄 **Docs/Media**: full-page screenshots (scroll-stitched), HTML→MD, PDF extract/OCR, PDF invoice/merge, MD→PDF, strip EXIF/metadata, site tech report
- 🎙️ **Speech**: **Kokoro-82M neural TTS** (30+ voices, $0.004/1k chars), STT (Whisper, $0.006/min)
- 🌐 **External**: video download/MP3 per-minute (no cap), email verify, reverse DNS, geoip, temp webhook
- 🖼️ **Utils**: image compress (88% savings), base64/JSON/CSV tools

**For agents (MCP — easiest path):**
```json
{
  "mcpServers": {
    "ox402-utils": { "url": "https://satisfaction-genetic-lightbox-buying.trycloudflare.com/mcp402/" }
  }
}
```

**For humans (CLI):**
```bash
npm i -g x402
export X402_PRIVATE_KEY=0x...
x402 curl https://satisfaction-genetic-lightbox-buying.trycloudflare.com/x402/paid/crypto-price \
  -H 'Content-Type: application/json' -d '{"ids":"bitcoin,ethereum"}'
```

**Pricing**: $0.001–$0.10/call. First call ~$0.004. No free trial, no signup, no API keys — just x402.

Live: https://satisfaction-genetic-lightbox-buying.trycloudflare.com
GitHub: https://github.com/Hasned-spec/ox402-utils
Discovery: `/.well-known/x402` + `/llms.txt` (agent-crawler friendly)

Feedback welcome — happy to add tools agents actually need.

---

## 2. r/x402 (Reddit) — reddit.com/r/x402
**Title**: [Launch] ox402-utils — 57 paid tools for AI agents via x402 (MCP ready, $0.004 first call)

**Body**:
Built a production x402 service with **57 tools** agents can actually use — things an agent can't do in its own sandbox (web research, security audits, full-page screenshots, neural TTS, video download, document processing, etc.).

**Key details:**
- **MCP server ready** — drop the URL into Claude/Cursor and the agent sees all 57 tools, pays per call automatically
- **Per-minute video pricing** ($0.004/min, no file-size cap) — transparent, no surprise bills
- **Kokoro-82M TTS** (offline, CPU, 30+ voices, $0.004/1k chars)
- **Full-page screenshots** via headless Chrome (scroll-stitched, not viewport crops)
- **Security pack**: SSL, headers, DNS, subdomains, threat intel, breach checks
- **Price range**: $0.001–$0.10/call. First call ~$0.004.
- **Discovery**: `/.well-known/x402` + `/llms.txt` live, listed on 402index

**Live**: https://satisfaction-genetic-lightbox-buying.trycloudflare.com
**MCP**: `https://satisfaction-genetic-lightbox-buying.trycloudflare.com/mcp402/`
**GitHub**: https://github.com/Hasned-spec/ox402-utils

The tunnel URL rotates — the site uses `location.host` dynamically so MCP/CTA links never go stale. The 15-min cron keeps 402index listings fresh and updates discovery files on rotation.

Built for agents first, humans second. No free tier (every call paid), no API keys, no signup.

Would love feedback from the x402 community — what tools are missing that agents actually need?

---

## 3. r/ethfinance (Reddit) — Weekly "Builder Wednesday" or Daily Discussion
**Title**: x402 in production: 57 paid tools for AI agents (MCP + x402, USDC on Base)

**Body**:
The agent economy needs infrastructure agents can actually pay for. Built **ox402-utils** — a utility grid of 57 tools (research, security, media, speech, external APIs) monetized via **x402 (USDC on Base)**.

**Why this matters for Eth/Base builders:**
- Agents can now **pay for capabilities they can't self-host** (browsers, heavy ML models, external APIs) without API keys or subscriptions
- **MCP-native** — one config line, agent gets 57 tools, pays per call
- **Per-use pricing** ($0.001–$0.10) matches agent economics — no $20/mo for 3 calls
- **Real neural TTS** (Kokoro-82M, offline CPU) + **full-page screenshots** (headless Chrome)
- **Security audits** agents can run on any domain (SSL, headers, DNS, threats)

Live: https://satisfaction-genetic-lightbox-buying.trycloudflare.com
MCP config:
```json
{ "mcpServers": { "ox402-utils": { "url": "https://satisfaction-genetic-lightbox-buying.trycloudflare.com/mcp402/" } } }
```

GitHub: https://github.com/Hasned-spec/ox402-utils

This is the "AWS for agents" moment — pay-per-call, no lock-in, on Base. Curious what the ethfinance builders think about agent-native monetization.

---

## 4. Base Discord (discord.gg/buildonbase) — #builders or #general
**Title**: 🚀 ox402-utils — 57 paid tools for agents on Base (x402 + MCP)

**Body**:
Launched on Base: **ox402-utils** — 57 tools agents pay for per-call via x402 (USDC).

**What agents get:**
- Web research, deep briefs, repo→context
- Security: SSL, headers, DNS, subdomains, threats
- Media: full-page screenshots, PDF extract/OCR, video→MP3 (per-min), HTML→MD
- **Neural TTS** (Kokoro-82M, 30+ voices, offline)
- Utils: image compress, base64/JSON/CSV, email verify, geoip

**MCP (1 line):**
```json
{ "mcpServers": { "ox402-utils": { "url": "https://satisfaction-genetic-lightbox-buying.trycloudflare.com/mcp402/" } } }
```

**CLI:**
```bash
npm i -g x402 && export X402_PRIVATE_KEY=0x...
x402 curl https://satisfaction-genetic-lightbox-buying.trycloudflare.com/x402/paid/crypto-price -d '{"ids":"bitcoin,ethereum"}'
```

$0.001–$0.10/call. First call ~$0.004. No signup, no keys.

Live + GitHub in thread. Built on Base, for agents. 🟦

---

## 5. Telegram x402 Builders (t.me/x402builders)
**Message**:
🚀 **ox402-utils** — 57 paid tools for AI agents via x402 (USDC on Base)

✅ MCP server: `https://satisfaction-genetic-lightbox-buying.trycloudflare.com/mcp402/`
✅ x402 discovery: `/.well-known/x402` + `/llms.txt`
✅ Per-minute video pricing, no cap
✅ Kokoro-82M neural TTS (offline)
✅ Full-page screenshots (scroll-stitched)
✅ Security pack: SSL, DNS, threats, breaches
✅ $0.001–$0.10/call, first call ~$0.004

GitHub: https://github.com/Hasned-spec/ox402-utils
Live: https://satisfaction-genetic-lightbox-buying.trycloudflare.com

Drop the MCP URL into your agent — it just works. No API keys, no free tier, pure x402.

---

## 6. Warpcast /x402 channel
**Cast**:
Just launched ox402-utils — 57 paid tools for agents on Base via x402.

MCP: `https://satisfaction-genetic-lightbox-buying.trycloudflare.com/mcp402/`
Live: `https://satisfaction-genetic-lightbox-buying.trycloudflare.com`

Kokoro TTS • full-page screenshots • per-min video • security audits • web research
$0.001–$0.10/call. No signup, no keys. Pure agent economy. 🟦

#x402 #Base #MCP #AgentEconomy

---

## 7. x402 Foundation Discord (discord.gg/x402) — #showcase or #general
Same as #1 but tagged for showcase.

---

## 8. Twitter/X (@x402org reply + own tweet)
**Tweet**:
Built ox402-utils: 57 tools agents pay for per-call via x402 (USDC on Base).

MCP ready: drop `https://satisfaction-genetic-lightbox-buying.trycloudflare.com/mcp402/` into your agent.

Kokoro-82M TTS • scroll-stitched screenshots • per-min video • security audits
$0.004 first call. No signup, no keys. Just x402.

https://github.com/Hasned-spec/ox402-utils

@x402org @buildonbase #x402 #Base #MCP #AgentEconomy

---

## 9. Awesome-x402 submission (GitHub PR to xpaysh/awesome-x402)
**PR title**: Add ox402-utils — 57 paid tools for agents (MCP + x402)

**Body**:
Service: https://satisfaction-genetic-lightbox-buying.trycloudflare.com
MCP: `/mcp402/`
57 tools: research, security, media, speech, external APIs
Pay-to: `0x7869d1fe2d1de863b6fae4594d392343a69ed8e3` (USDC on Base)
Pricing: $0.001–$0.10/call
Discovery: `/.well-known/x402` + `/llms.txt` live
GitHub: https://github.com/Hasned-spec/ox402-utils

---

## 10. TOLL·402 (toll402.com) — they auto-index, but can try to submit
Their indexer scrapes x402.org/ecosystem and awesome-x402. Submitting to those covers it.