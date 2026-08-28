#!/usr/bin/env python3
"""ox402 seller v4: x402-paid agent tools (Base USDC). High-friction capabilities
AI agents can't replicate with local compute. Free trial: 5 calls/IP on tier=free tools; paid-tier tools always require payment."""
import base64, json, os, re, time, urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import x402_security as SEC
import x402_tools as T1
import x402_tools2 as T2
import x402_tools3 as T3
import x402_tools4 as T4
import x402_tools5 as T5
import x402_tools6 as T6
import x402_tools7 as T7
import x402_tools8 as T8
import x402_tools9 as T9
import x402_tools10 as T10
import x402_tools11 as T11
import x402_tools12 as T12
import x402_tools13 as T13
import x402_tools14 as T14
import x402_tools15 as T15
import x402_tools16 as T16
import x402_tools17 as T17

PORT = int(os.environ.get('OX402_PORT', '8793'))
NETWORK = 'eip155:8453'  # Base mainnet
W = {'address': os.environ.get('OX402_PAYTO', '0xE9C9cC258f7137fD0AbA4Ae513F0Cfa288c0cDc9')}
# Self-hosted x402 facilitator (no CDP key needed): verifies + settles USDC on Base.
FACILITATOR = os.environ.get('OX402_FACILITATOR', 'http://127.0.0.1:8090')

# tool_name -> (function, price_usd, tier, description, sample)
# tier 'free' = first FREE_TRIAL_CALLS calls/IP are free; 'paid' = never free.
TOOLS = {
    # ---- research & web intelligence ----
    'search':        (T4.tool_search, 0.008, 'free', 'Read-only web search (DuckDuckGo): title+url+snippet per result. Cost $0.008/call.', {'query':'x402 protocol','count':5}),
    'html2md':       (T4.tool_html2md, 0.008, 'free', 'Extracts clean Markdown from any public URL (no raw DOM noise). Read-only.', {'url':'https://example.com'}),
    'web-scrape':    (T2.tool_web_scrape, 0.01, 'free', 'Server-side URL scrape returning title + readable text. Use when you need plain text fast. Read-only.', {'url':'https://example.com'}),
    'extract-structured': (T9.tool_extract_structured, 0.02, 'free', 'Structured Web Data Extractor: fetch a URL, return JSON matching your schema via a fast LLM. Read-only. Cost ~$0.02.', {'url':'https://news.ycombinator.com','schema':{'type':'object','properties':{'top_stories':{'type':'array','items':{'type':'object','properties':{'title':{'type':'string'}}}}}}}),
    'whois':         (T4.tool_whois, 0.01, 'free', 'Domain WHOIS: registrar, creation/expiry dates, nameservers, availability. Read-only.', {'domain':'google.com'}),
    'dns-lookup':    (T4.tool_dns, 0.005, 'free', 'DNS records A/AAAA/MX/NS/TXT/CNAME for a domain. Read-only.', {'domain':'github.com','types':['A','MX']}),

    # ---- documents & media conversion ----
    'pdf-extract':   (T2.tool_pdf_extract, 0.02, 'free', 'Extracts text from PDF URLs or base64. Agents lack poppler/pdftotext; we run it server-side.', {'url':'https://arxiv.org/pdf/1706.03762'}),
    'ocr':           (T4.tool_ocr, 0.02, 'free', 'OCR image to text (Tesseract; url or base64 input). Handles screenshots/scans/photos of text.', {'url':'https://x.com/img.png','lang':'eng'}),
    'md2pdf':        (T8.tool_md2pdf, 0.02, 'free', 'Markdown to styled PDF document (tables/headings supported). Returns base64 PDF. Non-destructive.', {'title':'Report','markdown':'# Hi\n\nHello **world**'}),
    'pdf-invoice':   (T5.tool_pdf_invoice, 0.02, 'free', 'Generate invoice/receipt PDF from line items (seller, buyer, tax). Returns base64 PDF.', {'from_name':'ox402','to_name':'Acme','items':[{'desc':'Work','qty':1,'unit_price':100}]}),
    'pdf-merge':     (T14.tool_pdf_merge, 0.02, 'free', 'Combine multiple PDFs into one (pass list of base64 PDFs). Contracts, reports, scans.', {'pdfs':['<b64#1>','<b64#2>']}),
    'stt':           (T8.tool_stt, 0.006, 'free', 'Speech-to-text via Whisper-large-v3: timestamped transcript from audio URL/base64. Billed $0.006 per started minute. Free trial caps at 5 min/file; paid allows 25MB/file up to 120 min. Premium accuracy.', {'url':'https://x.com/talk.mp3'}),
    'stt-fast':      (T8.tool_stt_fast, 0.002, 'free', 'Fast local speech-to-text (whisper-tiny): cheap transcript for clear audio. Billed $0.002 per started minute. Free trial caps at 5 min/file. Less accurate than stt.', {'url':'https://x.com/talk.mp3'}),
    # ---- speech & local generative (all CPU / offline) ----
    'tts':           (T15.tool_tts, 0.004, 'paid', 'Neural text-to-speech via Kokoro-82M (real neural TTS, 30+ English voices, runs offline on CPU). WAV base64. Billed $0.004 per 1k chars (<=4000 chars/call). Falls back to espeak-ng if model unavailable. Voices via tts-voices.', {'text':'Hello from ox402, this is a neural voice.','voice':'af_heart','speed':1.0}),
    'tts-voices':     (T15.tool_tts_voices, 0.0, 'paid', 'List available Kokoro neural voices (af_*/am_* = US English, bf_*/bm_* = UK English). Free reference call.', {'language':'en'}),

    # ---- video & audio download ----

    'video-info':    (T6.tool_video_info, 0.008, 'free', 'Video metadata + all stream formats (YouTube/TikTok/Vimeo/X/1000+ sites) via yt-dlp. Read-only.', {'url':'https://www.tiktok.com/@scout2015/video/6718335390845095173'}),
    'video-download':(T6.tool_video_download, 0.004, 'free', 'Direct download links for any video URL (yt-dlp, 1000+ platforms). Priced per-minute of the source (~$0.0004/min) — reports source duration. No file-size cap.', {'url':'https://www.tiktok.com/@scout2015/video/6718335390845095173','max_height':'720'}),

    # ---- finance / geo / weather ----
    'crypto-price':  (T4.tool_crypto, 0.004, 'free', 'Crypto spot prices + 24h change (CoinGecko ids). Read-only.', {'ids':'bitcoin,ethereum,solana'}),
    'stock-quote':   (T4.tool_quote, 0.005, 'free', 'Stock quote: last price, prev close, exchange (Yahoo Finance). Read-only.', {'symbol':'AAPL'}),
    'fx-rates':      (T4.tool_fx, 0.004, 'free', 'Fiat FX rates (ECB daily reference). Read-only.', {'base':'USD','symbols':'EUR,GBP,JPY'}),
    'weather':       (T4.tool_weather, 0.004, 'free', 'Current weather + 3-day forecast by city or coords. Read-only.', {'place':'Miami'}),
    'geoip':         (T4.tool_geoip, 0.005, 'free', 'IP geolocation: country/city/ISP/proxy/hosting flags. Read-only.', {'ip':'1.1.1.1'}),

    # ---- compute sandbox ----
    'exec-python':   (T8.tool_exec_python, 0.02, 'free', 'Isolated Python 3.12 sandbox: run a snippet with {"payload":...,"input":...} globals, capture stdout + result var. CPU/RAM-capped, no network. Mutating only inside sandbox.', {'code':'result = sum(payload["nums"])','payload':{'nums':[1,2,3]}}),

    # ---- agent utility pack ----
    'repo2context':  (T10.tool_repo2context, 0.015, 'free', 'GitHub repo -> single LLM-ready context file: clones, strips lockfiles/binaries/minified, packs source into markdown. Size-capped.', {'repo_url':'https://github.com/owner/repo','max_kb':250}),
    'md-compress':   (T10.tool_md_compress, 0.008, 'free', 'Compress scraped/markdown text for prompts: strips base64 blobs, tracking pixels, dup lines, whitespace runs. Typically 30-50% smaller.', {'text':'<pasted page text>'}),
    'temp-webhook':  (T10.tool_temp_webhook, 0.005, 'free', 'Ephemeral public webhook URL (1h TTL): POST anything to it, then poll the same URL to read payloads. No server needed.', {'ttl_minutes':60}),
    'video2mp3':     (T10.tool_video2mp3, 0.004, 'free', 'Video/audio URL -> clean mono MP3 (48kbps, yt-dlp + ffmpeg, 1000+ platforms). Billed per started minute at $0.0004/min, reports minutes_billed. No file-size cap. Platform blocks may apply (YouTube/Vimeo need auth).', {'url':'https://example.com/podcast-ep.mp4','max_seconds':3600}),
    'image-optimize':(T10.tool_image_optimize, 0.01, 'free', 'Convert heic/png/jpeg -> webp/jpeg/png with compression + optional max_width resize. Reports saved %.', {'url':'https://x.com/photo.heic','format':'webp','quality':80}),
    'image-compress':(T13.tool_image_compress, 0.001, 'free', 'Cheap image shrink: resize to a max dimension + quality, returns smaller base64. For trimming payloads before you send them on. Returns saved %.', {'image_base64':'<b64>','max_dimension':1280,'quality':75}),
    'link-scan':     (T10.tool_link_scan, 0.01, 'free', 'URL safety scan: full redirect chain, tracking-param strip, urlhaus+openphish feeds, SSL validity, phishing-form heuristic, risk score.', {'url':'https://bit.ly/xyz'}),
    'file-scan':     (T10.tool_file_scan, 0.02, 'free', 'Static file analysis (nothing executed): sha256 vs MalwareBazaar, YARA rules, entropy, PDF active-content, PE imports/sections, archive entry listing. <=25MB.', {'file_base64':'<b64>','filename':'invoice.pdf'}),

    # ---- high-utility offline pack (T11) ----
    'http-headers':  (T11.tool_http_headers, 0.004, 'free', 'HTTP response status + full headers for a URL. Read-only.', {'url':'https://example.com'}),
    'ssl-check':     (T11.tool_ssl_check, 0.006, 'free', 'TLS certificate validity, expiry (days), issuer, SANs for a host:443. Read-only.', {'host':'github.com'}),
    'sitemap':       (T11.tool_sitemap, 0.006, 'free', 'Fetch + parse a sitemap.xml, list URLs (and nested maps).', {'url':'https://example.com'}),
    'robots':        (T11.tool_robots, 0.005, 'free', 'Fetch robots.txt and return structured allow/disallow rules.', {'url':'https://example.com'}),

# ---- restored 2026-08-25: classic utility pack (T1) + csv/json pack (T3) ----
    # ---- text & data utilities ----
    'base64':        (T1.tool_base64, 0.005, 'free', 'Base64 encode/decode of text (mode=decode for the reverse). Instant.', {'data':'hello world'}),
    'base64-url':    (T3.tool_base64_files, 0.02, 'free', 'Fetch a file from a URL (<=25MB) and return it as base64 data-url. Read-only.', {'url':'https://example.com/img.png'}),
    'csv2json':      (T1.tool_csv2json, 0.005, 'free', 'Convert CSV text to JSON array of row objects. Handles quoted fields via csv module.', {'csv':'name,age\\nAda,36\\nAlan,41'}),
    'json2csv':      (T3.tool_json2csv, 0.005, 'free', 'Convert JSON array of flat objects to CSV text. Column union across rows.', {'json':'[{"name":"Ada","age":36}]'}),
    'csv-col':       (T3.tool_csv_col, 0.005, 'free', 'Extract one column from CSV text as a list. Fast column slice.', {'csv':'name,age\\nAda,36','col':'name'}),
    'csv-sum':       (T1.tool_csv_sum, 0.005, 'free', 'Sum a numeric column across CSV rows. Non-numeric treated as 0.', {'csv':'item,cost\\na,1.5\\nb,2','col':'cost'}),
    'sort-json':     (T3.tool_sort_json, 0.005, 'free', 'Sort a JSON array of objects by key (asc/desc).', {'json':'[{"n":2},{"n":1}]','key':'n'}),
    'unique':        (T3.tool_unique, 0.005, 'free', 'Deduplicate lines or list items, preserving first-seen order. Returns count too.', {'items':['a','b','a']}),
    'regex-extract': (T1.tool_regex_extract, 0.005, 'free', 'Extract all regex matches from text. Quick pattern pulls without writing code.', {'pattern':'[0-9]+','text':'abc 123 def 456'}),

    # ---- dev utilities ----
    'hash':          (T1.tool_hash, 0.005, 'free', 'Hash text with sha256/sha1/md5/any hashlib algo. Deterministic digests.', {'algo':'sha256','data':'hello'}),
    'uuid':          (T1.tool_uuid, 0.005, 'free', 'Generate random UUID v4. One per call.', {}),
    'jwt-decode':    (T1.tool_jwt_decode, 0.005, 'free', 'Decode JWT header+payload (no signature verification). Debug tokens safely.', {'token':'eyJhbG...xIn0.x'}),
    'timestamp':     (T1.tool_timestamp, 0.005, 'free', 'Unix epoch <-> ISO8601 conversion, both directions, auto-detected.', {'value':1700000000}),
    'unit-convert':  (T1.tool_unit_convert, 0.005, 'free', 'Convert length/mass units (m/ft/km/mi/kg/lb/g/oz...). Simple physical units.', {'value':10,'from':'km','to':'mi'}),
    'diff':          (T1.tool_diff, 0.005, 'free', 'Unified diff of two texts (a vs b). Line-level changes at a glance.', {'a':'one\\ntwo','b':'one\\nTHREE'}),
    'json-format':   (T1.tool_json_format, 0.005, 'free', 'Pretty-print/minify JSON with chosen indent. Validate + format in one call.', {'json':'{"a":1}','indent':2}),
    'json-merge':    (T1.tool_json_merge, 0.005, 'free', 'Deep-merge two JSON objects (b wins on conflicts). Config layering.', {'a':{'x':{'y':1}},'b':{'x':{'z':2}}}),
    'qrcode':        (T1.tool_qrcode, 0.005, 'free', 'QR code PNG from any text/url, returned as data-url. Scan-ready instantly.', {'data':'https://ox402.io'}),

    # ---- image from text ----
    'text2img':      (T4.tool_text2img, 0.01, 'free', 'Render text to PNG image (PIL): custom width/font size, dark or light theme. No diffusion.', {'text':'Hello ox402','width':800,'font_size':24,'dark':True}),

    # ---- security & recon (T12) ----
    'security-headers': (T12.tool_security_headers, 0.01, 'free', 'Grade a sites HTTP security headers (HSTS/CSP/X-Frame-Options/XXP/Referrer-Policy/Permissions-Policy). A-D grade.', {'url':'https://github.com'}),
    'cors-check':    (T12.tool_cors_check, 0.008, 'free', 'Probe a URL CORS policy from a fake origin: detect wildcard/credentialed cross-origin holes.', {'url':'https://api.example.com','origin':'https://evil.example.com'}),
    'cookie-flags':   (T12.tool_cookie_flags, 0.006, 'free', 'Parse Set-Cookie for Secure/HttpOnly/SameSite flags; list insecure or JS-readable cookies.', {'url':'https://example.com'}),
    'dns-recon':     (T12.tool_dns_recon, 0.008, 'free', 'Full DNS recon: A/AAAA/MX/NS/TXT/CNAME/SOA + SPF/DKIM/DMARC email-auth presence.', {'domain':'github.com'}),
    'port-scan':     (T12.tool_port_scan, 0.01, 'free', 'TCP connect scan of common ports (honest: one datacenter vantage, not stealth).', {'host':'example.com','ports':[80,443,22,3389]}),
    'leak-check':    (T12.tool_leak_check, 0.01, 'free', 'Email against HaveIBeenPwned k-anonymity range API: breached? how many times?', {'email':'test@example.com'}),
    'subdomain-find':(T12.tool_subdomain_find, 0.01, 'free', 'Passive subdomain discovery via crt.sh certificate transparency (no probing).', {'domain':'github.com'}),
    'threat-intel':  (T12.tool_threat_intel, 0.01, 'free', 'IP reputation: DNSBL blacklist hits + proxy/VPN/Tor + geo (ipwho.is). Verdict clean/suspicious.', {'ip':'1.1.1.1'}),
    'capture-page':  (T13.tool_capture_page, 0.06, 'free', 'Full-page screenshot and/or PDF of any URL via headless Chromium. Developers, agents, and users needing clean captures + PDF receipts without running a browser. Returns base64.', {'url':'https://example.com','format':'png','full':True,'width':1280}),
    'strip-metadata':(T13.tool_strip_metadata, 0.10, 'free', 'Privacy scrubber: removes EXIF/GPS/comments from images and metadata from PDFs. One call before you post or share.', {'image_base64':'<b64>','filename':'photo.jpg'}),
    'site-report':   (T13.tool_site_report, 0.08, 'free', 'One-call website security + SSL audit: cert expiry/issuer, missing security headers, load speed. For site owners + devs.', {'url':'https://example.com'}),
    'email-verify':  (T14.tool_email_verify, 0.01, 'free', 'Email deliverability check: syntax + MX record presence + disposable-domain flag. DNS only, no send.', {'email':'foo@gmail.com'}),
    'reverse-dns':   (T14.tool_reverse_dns, 0.006, 'free', 'Reverse DNS: IP -> PTR hostname. Confirms what a server calls itself.', {'ip':'8.8.8.8'}),
    'header-compare':(T14.tool_header_compare, 0.01, 'free', 'Compare security headers of two sites side by side (HSTS/CSP/XFO/XXP/RP/PP). Migration + audit aid.', {'url_a':'https://github.com','url_b':'https://gitlab.com'}),
    'screenshot-mobile': (T14.tool_screenshot_mobile, 0.06, 'free', 'Mobile-viewport (390x844) screenshot and/or PDF of a URL via headless Chromium. Responsive check without a device.', {'url':'https://example.com','format':'png'}),

    # ---- deep research (T12) ----
    'deep-search':    (T12.tool_deep_search, 0.012, 'free', 'Multi-query fan-out search: dedupe + rank results across 5 queries. Agent-grade discovery.', {'query':'best x402 payment providers','also':['x402 tutorial','coinbase x402']}),
    'research-brief': (T12.tool_research_brief, 0.02, 'free', 'Topic -> search + fetch top sources -> markdown dossier with citations. Research on autopilot.', {'topic':'nvidia nim alternatives'}),
    'citations':      (T12.tool_citations, 0.015, 'free', 'Fetch N URLs, return canonical BibTeX cites + cleaned text (RAG-ready corpus).', {'urls':['https://example.com/a','https://example.com/b']}),
    'fact-check':     (T12.tool_fact_check, 0.012, 'free', 'Claim -> search corroborating/contradicting sources, return verdict (corroborated/contradicted/mixed).', {'claim':'drinking coffee reduces lifespan'}),
    'trend-watch':    (T12.tool_trend_watch, 0.01, 'free', 'Recent signal volume on a keyword across news/social slices. Early-trend radar.', {'keyword':'ai agents'}),
    'web-archive':    (T14.tool_web_archive, 0.006, 'free', 'Fetch the latest Wayback Machine snapshot for any URL. Recover changed/dead pages.', {'url':'example.com'}),
    'link-health':    (T14.tool_link_health, 0.02, 'free', 'Crawl a page, report status of every outbound link (broken 4xx/5xx/timeout). Pre-publish link check.', {'url':'https://example.com'}),

    # ---- PREMIUM human-attractive tools (T16) ----
    'ai-text':       (T16.tool_ai_text, 0.03, 'paid', 'AI chatbot / text generation: ask anything, get a useful answer (free LLM). For humans who want a quick assistant without signing up. $0.03/call.', {'prompt':'Explain x402 in one sentence','system':'You are a helpful assistant.'}),
    'ai-rewrite':    (T16.tool_ai_rewrite, 0.03, 'paid', 'AI rewriter / humanizer: makes text sound natural and human (kills AI-slop). Students, marketers, founders love this. $0.03/call.', {'text':'The implementation leverages synergistic paradigms to optimize outcomes.','style':'natural, human, fluent'}),
    'ai-summarize':  (T16.tool_ai_summarize, 0.03, 'paid', 'AI summarizer: turns long text into 3-5 bullet points. Articles, docs, meeting notes. $0.03/call.', {'text':'Paste a long article or report here...'}),
    'translate':     (T16.tool_translate, 0.03, 'paid', 'Translate text between 100+ languages (LibreTranslate / MyMemory). No API key. $0.03/call.', {'text':'Hello, how are you?','from':'en','to':'es'}),
    'resume-parse':  (T16.tool_resume_parse, 0.03, 'paid', 'Resume / CV parser: PDF -> structured JSON (name, email, phone, skills). Job-seekers and recruiters. $0.03/call.', {'url':'https://example.com/resume.pdf'}),
    'pdf-to-word':   (T16.tool_pdf_to_word, 0.04, 'paid', 'Convert a PDF into an editable Word (.docx) file. $0.04/call.', {'url':'https://example.com/doc.pdf'}),
    'plagiarism':    (T16.tool_plagiarism, 0.04, 'paid', 'Plagiarism / web-similarity check: estimates how much of your text already exists online. Students + writers. $0.04/call.', {'text':'Paste your essay or article here...'}),
    'qr':            (T16.tool_qr, 0.001, 'paid', 'QR code generator: any text/url -> scannable PNG. $0.001/call.', {'data':'https://ox402.io'}),
    'link-preview':  (T16.tool_link_preview, 0.01, 'paid', 'Link unfurl / preview card: Open Graph title+description+image for any URL (like a social embed). $0.01/call.', {'url':'https://github.com'}),
    'pdf-compress':  (T16.tool_pdf_compress, 0.03, 'paid', 'Shrink a PDF (re-pack pages, drop bloat). Email-friendly. $0.03/call.', {'url':'https://example.com/big.pdf'}),
    'video-thumb':   (T16.tool_video_thumb, 0.02, 'paid', 'Extract a thumbnail frame from any video URL at a given timestamp (ffmpeg). $0.02/call.', {'url':'https://example.com/clip.mp4','at':1}),

    # ---- high-demand agent utilities (T17) ----
    'openapi-fetch': (T17.tool_openapi_fetch, 0.008, 'free', 'Fetch + parse OpenAPI/Swagger spec from URL, return endpoint summary. Agent API discovery.', {'url':'https://api.example.com/openapi.json'}),
    'graphql':       (T17.tool_graphql, 0.01, 'free', 'GraphQL introspection or query execution. Pass introspect=true for schema, or query+variables to run.', {'url':'https://api.example.com/graphql','introspect':True}),
    'sqlite':        (T17.tool_sqlite, 0.01, 'free', 'In-memory SQLite sandbox: run SQL on CSV data you provide. Read-only by default; allow_write=true for DML.', {'sql':'SELECT * FROM users WHERE age > 25','csv_data':[{'table':'users','csv_text':'name,age\\nAda,36\\nAlan,41'}]}),
    'embed':         (T17.tool_embed, 0.01, 'free', 'Local embeddings (BAAI/bge-small) + optional similarity search against provided docs. CPU, no API.', {'texts':['hello','world'],'docs':[{'id':1,'text':'greeting'}]}),
    'price-estimate':(T17.tool_price_estimate, 0.0, 'free', 'Cost estimator: pass calls [{tool, count}] -> USD total + free-trial breakdown. No charge, helps agents budget.', {'calls':{'search':5,'pdf-extract':2}}),
    'dry-run':       (T17.tool_dry_run, 0.0, 'free', 'Preview a tool call: returns 402 challenge structure + price without payment. Use before paying.', {'tool':'search'}),
    'batch':         (T17.tool_batch, 0.0, 'paid', 'Execute up to 10 tools in one payment (sum of prices). Pass calls: [{tool, input}]. Returns all results.', {'calls':[{'tool':'search','input':{'query':'x402'}},{'tool':'whois','input':{'domain':'google.com'}}]}),
}

def price_for(tool):
    return f"{TOOLS[tool][1]:.3f}"

def client_ip(headers, addr):
    # X-Forwarded-For is NOT trusted (spoofable by clients). Use socket peer
    # (unspoofable) or X-Real-IP only when set by our own proxy (caddy/cloudflared).
    return SEC.get_real_ip(headers, addr)

def public_base_url(headers=None):
    """Canonical public HTTPS origin for payment resources + catalog links."""
    env = os.environ.get('OX402_PUBLIC_URL')
    if env:
        return env.rstrip('/')
    host = None
    try:
        host = open('/home/opencode/forever-crypto/.tunnel_host').read().strip()
    except Exception:
        pass
    if headers:
        h = (headers.get('Host') or '').strip().lower()
        if h.endswith('.trycloudflare.com'):
            host = h
    if host:
        try:
            cur = open('/home/opencode/forever-crypto/.tunnel_host').read().strip()
        except Exception:
            cur = ''
        if cur != host:
            open('/home/opencode/forever-crypto/.tunnel_host', 'w').write(host)
        return f'https://{host}'
    return 'http://129.213.128.185'

# ---- free trial ledger: N free calls per IP, persisted so it survives restarts ----
FREE_TRIAL_CALLS = 10
_FREE_LEDGER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'free_trial.jsonl')

def _load_free():
    use = {}
    try:
        with open(_FREE_LEDGER) as f:
            for line in f:
                try:
                    r = json.loads(line)
                    use[r['ip']] = use.get(r['ip'], 0) + 1
                except Exception:
                    pass
    except FileNotFoundError:
        pass
    return use

_free_use = _load_free()

def free_remaining(ip):
    return max(0, FREE_TRIAL_CALLS - int(_free_use.get(ip, 0)))

def consume_free(ip):
    _free_use[ip] = _free_use.get(ip, 0) + 1
    try:
        with open(_FREE_LEDGER, 'a') as f:
            f.write(json.dumps({'t': time.time(), 'ip': ip}) + '\n')
    except Exception:
        pass

def verify_x402(headers, tool):
    hdr = headers.get('X-Payment') or headers.get('x-payment')
    if not hdr:
        return False, None, None, 'missing X-PAYMENT header'
    try:
        payload = json.loads(base64.b64decode(hdr))
    except Exception as e:
        return False, None, None, f'bad payment encoding: {e}'
    price = price_for(tool).lstrip('$')
    body = {'x402Version': payload.get('x402Version', 1), 'paymentHeader': hdr}
    req = urllib.request.Request(FACILITATOR + '/verify',
        data=json.dumps(body).encode(), method='POST',
        headers={'Content-Type': 'application/json'})
    try:
        res = json.load(urllib.request.urlopen(req, timeout=20))
    except Exception as e:
        return False, None, None, f'facilitator verify failed: {e}'
    if not res.get('isValid'):
        return False, None, None, 'payment invalid: ' + json.dumps(res.get('invalidReason'))
    def settle():
        sreq = urllib.request.Request(FACILITATOR + '/settle',
            data=json.dumps(body).encode(), method='POST',
            headers={'Content-Type': 'application/json'})
        return json.load(urllib.request.urlopen(sreq, timeout=20))
    return True, res.get('payer'), settle, None

class H(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _send(self, code, obj, extra=None, content_type='application/json'):
        b = json.dumps(obj).encode() if not isinstance(obj, bytes) else obj
        self.send_response(code)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', str(len(b)))
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, X-PAYMENT')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        for k, v in (extra or {}).items():
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(b)

    def do_OPTIONS(self):
        return self._send(204, b'', content_type='text/plain')

    def _hook(self, hid):
        """Ephemeral webhook capture: POST stores payload, GET polls."""
        ln = int(self.headers.get('Content-Length', 0) or 0)
        body = self.rfile.read(min(ln, 40 * 1024)) if self.command == 'POST' else b''
        code, out = T10.hook_capture(hid, self.command, body,
                                     self.headers.get('Content-Type', ''))
        return self._send(code, out)

    def challenge(self, tool):
        price = price_for(tool).lstrip('$')
        sample = TOOLS[tool][4]
        schema = {'type': 'object',
                  'properties': {k: {'type': 'string'} for k in sample.keys()},
                  'required': list(sample.keys())}
        pub = public_base_url(self.headers)
        chal = {'x402Version': 1, 'error': 'X402_PAYMENT_REQUIRED',
            'accepts': [{'scheme': 'exact', 'network': NETWORK,
                'maxAmountRequired': price,
                'resource': f'{pub}/x402/paid/{tool}',
                'description': 'ox402 utility call: ' + TOOLS[tool][3],
                'mimeType': 'application/json',
                'payTo': W['address'],
                'asset': '0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913',
                'maxTimeoutSeconds': 120, 'extra': {'name': 'USDC', 'version': '2'}}],
            'outputSchema': {'input': {'type': 'http', 'method': 'POST',
                'discoverable': True, 'bodyType': 'json', 'schema': schema,
                'example': sample}},
            'free_trial': {'calls_per_ip': FREE_TRIAL_CALLS, 'tier': 'free',
                           'note': 'First %d calls per IP are free on tier=free tools; paid-tier tools always require x402 USDC.' % FREE_TRIAL_CALLS}}
        b64 = base64.b64encode(json.dumps(chal).encode()).decode()
        self._send(402, chal, {'PAYMENT-REQUIRED': b64})

    def do_GET(self):
        m = re.match(r'^/hook/([\w-]{10,40})/?$', self.path)
        if m:
            return self._hook(m.group(1))
        if self.path.startswith('/health'):
            return self._send(200, {'ok': True, 'service': 'ox402-utils', 'version': 4,
                                    'tool_count': len(TOOLS), 'address': W['address']})
        if self.path == '/.well-known/x402' or self.path.startswith('/.well-known/x402?'):
            resources = [f'POST /x402/paid/{k}' for k in TOOLS]
            # CDP Bazaar discovery extension (per-resource metadata so agents can build valid calls)
            bazaar = {
                'version': 1,
                'resources': [
                    {
                        'method': 'POST',
                        'path': f'/x402/paid/{k}',
                        'description': v[3],
                        'price': f'${v[1]:.4f}'.rstrip('0').rstrip('.'),
                        'inputSchema': {'type': 'object', 'properties': {}},
                        'outputSchema': {'type': 'object'},
                    } for k, v in TOOLS.items()
                ],
            }
            return self._send(200, {'version': 1, 'resources': resources,
                'name': 'ox402-utils',
                'description': 'High-friction paid tools for AI agents: research, docs/media, STT/TTS per-minute, security scans, agent utilities. x402 USDC on Base. First 5 calls/IP free on tier=free tools.',
                'payment': {'scheme': 'exact', 'network': NETWORK,
                    'asset': '0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913',
                    'payTo': W['address']},
                'extensions': {'bazaar': bazaar}})
        if self.path.startswith('/.well-known'):
            # 402index domain-verification endpoint: serve the raw verification hash
            if self.path.endswith('/402index-verify.txt'):
                try:
                    import json as _j
                    _claim = _j.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '.402index_claim.json')))
                    _h = _claim.get('verification_hash', '')
                except Exception:
                    _h = ''
                return self._send(200, _h.encode(), content_type='text/plain')
            pub = public_base_url(self.headers)
            tools_manifest = []
            for k, v in TOOLS.items():
                sample = v[4]
                props = {pk: {'type': 'string', 'description': f'param {pk}'} for pk in sample.keys()}
                tools_manifest.append({
                    'id': k, 'price_usd': v[1], 'tier': v[2], 'desc': v[3],
                    'input_schema': {'type': 'object', 'properties': props,
                                     'required': list(sample.keys())},
                    'example': sample,
                })
            return self._send(200, {
                'schema_version': 'v1',
                'name': 'ox402-utils',
                'version': 4,
                'description': '87 paid micro-utilities for AI agents and humans, payable per call via x402 (USDC on Base). Free trial: 10 calls/IP on tier=free tools via /x402/trial/<tool> (no wallet, no signup).',
                'api': {'type': 'x402', 'url': f'{pub}/x402/paid', 'base_url': pub,
                        'free_trial_url': f'{pub}/x402/trial', 'mcp': f'{pub}/mcp402/'},
                'auth': {'type': 'x402', 'network': NETWORK, 'asset': 'USDC',
                         'payTo': W['address'],
                         'note': 'No API key. Each call returns a 402 with a payment requirement; pay via x402 and retry with the X-PAYMENT header.'},
                'contact': {'email': 'oxalpha413596@emalupe.com'},
                'legal': {'terms': f'{pub}/', 'privacy': f'{pub}/'},
                'tools': tools_manifest,
                'discovery': {'catalog': f'{pub}/x402/catalog', 'llms': f'{pub}/llms.txt'},
                'rail': 'x402'})
        if self.path.startswith('/x402/catalog') or self.path == '/catalog':
            return self._send(200, {'service': 'ox402-utils', 'version': 4,
                'tool_count': len(TOOLS), 'network': NETWORK, 'asset': 'USDC',
                'pay_to': W['address'],
                'free_trial': {'calls_per_ip': FREE_TRIAL_CALLS, 'tier': 'free'},
                'rate_limits': {'speech': '20 requests/min shared across stt/stt-fast/tts (all CPU)'},
                'tools': {k: {'price': v[1], 'tier': v[2], 'desc': v[3], 'sample': v[4]} for k, v in TOOLS.items()},
                'usage': 'POST /paid/<tool> JSON body; x402 402 handshake + X-PAYMENT header on every call. POST /trial/<tool> for 10 free calls/IP on tier=free tools (no payment).'})
        return self._send(200, {'service': 'ox402-utils', 'version': 4,
            'tool_count': len(TOOLS), 'price_from': 0.001, 'network': NETWORK, 'asset': 'USDC',
            'pay_to': W['address'],
            'endpoints': {'catalog': '/catalog', 'health': '/health', 'call': '/paid/<tool>'},
            'usage': 'GET /catalog for full schema+samples; POST /paid/<tool>; x402 payment required'})

    def do_POST(self):
        m = re.match(r'^/hook/([\w-]{10,40})/?$', self.path)
        if m:
            return self._hook(m.group(1))
        # --- free trial endpoint: /trial/<tool> or /x402/trial/<tool> runs tier=free tools free ---
        mt = re.match(r'/(x402/)?trial/([a-z0-9-]+)', self.path)
        if mt:
            tool = mt.group(2)
            if tool not in TOOLS:
                return self._send(404, {'error': 'unknown tool', 'hint': 'GET /catalog for the list'})
            fn, price, tier, desc, sample = TOOLS[tool]
            if tier != 'free':
                return self._send(402, {'error': 'paid-tier tool — use /x402/paid/<tool> with x402 payment',
                                        'note': 'Only tier=free tools are available on the trial endpoint.'})
            _ip = client_ip(self.headers, self.client_address)
            # Rate limit
            ok_rl, retry = SEC.rate_limit(_ip, tool)
            if not ok_rl:
                return self._send(429, {'error': 'rate limit exceeded', 'retry_after_seconds': retry})
            if free_remaining(_ip) <= 0:
                return self._send(402, {'error': 'X402_PAYMENT_REQUIRED',
                                        'note': f'Free trial exhausted for this IP ({FREE_TRIAL_CALLS} calls). Switch to /x402/paid/<tool> with an x402 USDC wallet.'})
            ln = int(self.headers.get('Content-Length', 0) or 0)
            try:
                body = json.loads(self.rfile.read(ln) or b'{}')
            except Exception:
                return self._send(400, {'error': 'bad JSON body'})
            body.pop('_free', None)
            consume_free(_ip)
            remaining = free_remaining(_ip)
            try:
                out = fn(body)
            except ValueError as e:
                return self._send(400, {'error': str(e)[:300]})
            except Exception as e:
                return self._send(500, {'error': 'tool error: ' + str(e)[:200]})
            with open(os.path.join(os.path.dirname(__file__), 'x402_sales.jsonl'), 'a') as f:
                f.write(json.dumps({'t': time.time(), 'tool': tool, 'tier': tier,
                                    'payer': 'free-trial', 'ok': True,
                                    'amount_usd': 0.0, 'amount': 0.0, 'free': True}) + '\n')
            return self._send(200, {'result': out, 'payer': 'free-trial', 'settled': True,
                                    'free_trial': True, 'free_calls_remaining': remaining,
                                    'note': f'Free trial call. {remaining} free calls left on this IP, then use /x402/paid/<tool> with x402 USDC.'})
        m = re.match(r'/(x402/)?paid/([a-z0-9-]+)', self.path)
        tool = m.group(2) if m else None
        if not tool or tool not in TOOLS:
            return self._send(404, {'error': 'unknown tool', 'hint': 'GET /catalog for the list'})
        fn, price, tier, desc, sample = TOOLS[tool]
        _ip = client_ip(self.headers, self.client_address)
        # Rate limit (paid calls also cost us compute; protect the box)
        ok_rl, retry = SEC.rate_limit(_ip, tool)
        if not ok_rl:
            return self._send(429, {'error': 'rate limit exceeded', 'retry_after_seconds': retry})
        ln = int(self.headers.get('Content-Length', 0) or 0)
        if ln > 8 * 1024 * 1024:  # 8MB hard cap on request body
            return self._send(413, {'error': 'payload too large (8MB max)'})
        try:
            body = json.loads(self.rfile.read(ln) or b'{}')
        except Exception:
            return self._send(400, {'error': 'bad JSON body'})
        body.pop('_free', None)  # never trust client-supplied flags

        ok, payer, settle, err = verify_x402(self.headers, tool)
        if not ok and err and err.startswith('missing'):
            return self.challenge(tool)
        if not ok:
            return self._send(402, {'error': err})
        try:
            out = fn(body)
        except ValueError as e:
            return self._send(400, {'error': str(e)[:300]})
        except Exception as e:
            return self._send(500, {'error': 'tool error: ' + str(e)[:200]})
        try:
            st = settle()
        except Exception as e:
            st = {'success': None, 'error': str(e)[:120]}
        amt = float(price)
        with open(os.path.join(os.path.dirname(__file__), 'x402_sales.jsonl'), 'a') as f:
            f.write(json.dumps({'t': time.time(), 'tool': tool, 'tier': tier, 'payer': payer,
                                'ok': st.get('success'), 'amount_usd': amt, 'amount': amt}) + '\n')
        self._send(200, {'result': out, 'payer': payer, 'settled': st.get('success')})

if __name__ == '__main__':
    SEC.install_ssrf_firewall()
    print(f"ox402 v4 on :{PORT} | tools={len(TOOLS)} | payTo={W['address']} | free trial: {FREE_TRIAL_CALLS} calls/IP on tier=free")
    ThreadingHTTPServer(('127.0.0.1', PORT), H).serve_forever()
