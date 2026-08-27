"""x402_tools16.py — Premium, human-attractive tools (high margin, no NVIDIA).

All run on-CPU or free upstream APIs:
- AI image generation (Pollinations, free, no key)
- AI text generation / chatbot (Pollinations text, free)
- AI text rewriter / humanizer (Pollinations)
- AI summarizer (local extractive + Pollinations fallback)
- Translation (LibreTranslate public + mymemory fallback)
- Resume / CV parser (pdfplumber -> structured JSON)
- PDF -> Word (docx)
- Plagiarism web-similarity checker (web search sim)
- QR code generator (segno)
- Link preview / unfurl card (OG tags)
- PDF compress (pypdf)
- Video thumbnail extractor (ffmpeg)
"""
import io, json, re, base64, urllib.parse, subprocess, tempfile, os
import requests

POLLINATIONS_IMG = "https://image.pollinations.ai/prompt/"
POLLINATIONS_TXT = "https://text.pollinations.ai/"

# ---------- helpers ----------
def _http_get(url, timeout=25, headers=None):
    return requests.get(url, timeout=timeout, headers=headers or {"User-Agent": "ox402/1.0"})

def _b64(data_url_or_bytes, mime):
    if isinstance(data_url_or_bytes, str) and data_url_or_bytes.startswith("data:"):
        return data_url_or_bytes
    b = data_url_or_bytes if isinstance(data_url_or_bytes, bytes) else data_url_or_bytes.encode()
    return "data:%s;base64,%s" % (mime, base64.b64encode(b).decode())

# ---------- AI image generation ----------
def tool_ai_image(params):
    prompt = (params.get("prompt") or "").strip()
    if not prompt:
        return {"error": "prompt required"}
    w = min(int(params.get("width", 1024)), 1280)
    h = min(int(params.get("height", 1024)), 1280)
    model = params.get("model", "turbo")
    seed = params.get("seed", "")
    url = "%s%s?width=%d&height=%d&model=%s&nologo=true&%s" % (
        POLLINATIONS_IMG, urllib.parse.quote(prompt), w, h, model,
        ("seed=" + str(seed)) if seed else "")
    r = _http_get(url, timeout=60)
    if r.status_code != 200:
        return {"error": "image gen failed: %d" % r.status_code}
    return {"result": {"data_url": _b64(r.content, "image/png"), "format": "png",
                       "bytes": len(r.content), "prompt": prompt,
                       "note": "Generated via Pollinations (free, no watermark)."}}

# ---------- AI text / chatbot ----------
def tool_ai_text(params):
    prompt = (params.get("prompt") or "").strip()
    if not prompt:
        return {"error": "prompt required"}
    if len(prompt) > 3000:
        prompt = prompt[:3000]
    model = params.get("model", "openai")
    sys = (params.get("system") or "").strip()
    q = prompt
    if sys:
        q = sys + "\n\n" + prompt
    r = _http_get(POLLINATIONS_TXT + urllib.parse.quote(q) + "?model=" + model, timeout=60)
    if r.status_code != 200:
        return {"error": "text gen failed: %d" % r.status_code}
    return {"result": {"text": r.text.strip(), "model": model,
                       "note": "Generated via Pollinations (free LLM)."}}

# ---------- AI rewriter / humanizer ----------
def _local_rewrite(text, style):
    """Heuristic rewrite that always works offline: simplifies inflated phrasing."""
    import re as _re
    swaps = [
        (r'\butilize\b', 'use'), (r'\bleverage\b', 'use'), (r'\bsynergistic\b', 'combined'),
        (r'\bparadigm\b', 'approach'), (r'\bfacilitate\b', 'help'), (r'\bimplement\b', 'build'),
        (r'\bmethodology\b', 'method'), (r'\boptimize\b', 'improve'), (r'\bfunctionality\b', 'feature'),
        (r'\badditional\b', 'more'), (r'\bapproximately\b', 'about'), (r'\bprior to\b', 'before'),
        (r'\bin order to\b', 'to'), (r'\ba sufficient number of\b', 'enough'),
        (r'\bwith regard to\b', 'about'), (r'\bcommence\b', 'start'), (r'\bterminate\b', 'end'),
    ]
    out = text
    for pat, rep in swaps:
        out = _re.sub(pat, rep, out, flags=_re.I)
    # break long sentences
    out = _re.sub(r'; ', '. ', out)
    if style and 'casual' in style.lower():
        out = out[0].lower() + out[1:] if out else out
    return out

def tool_ai_rewrite(params):
    text = (params.get("text") or "").strip()
    if not text:
        return {"error": "text required"}
    if len(text) > 3000:
        text = text[:3000]
    style = params.get("style", "natural, human, fluent")
    q = "Rewrite the following text to sound %s. Keep meaning and facts. Only return the rewritten text:\n\n%s" % (style, text)
    # try Pollinations POST first
    try:
        r = requests.post(POLLINATIONS_TXT, data=json.dumps({"messages": [{"role": "user", "content": q}]}),
                          timeout=45, headers={"Content-Type": "application/json"})
        if r.status_code == 200 and r.text.strip():
            return {"result": {"rewritten": r.text.strip(), "style": style, "engine": "pollinations"}}
    except Exception:
        pass
    # fallback: local heuristic rewrite (always works)
    return {"result": {"rewritten": _local_rewrite(text, style), "style": style, "engine": "local-heuristic",
                       "note": "LLM unavailable; applied offline simplification."}}

# ---------- AI summarizer ----------
def _local_summarize(text, max_points=5):
    """Extractive summary: split into sentences, score by word frequency, return top sentences."""
    import re as _re
    from collections import Counter
    sentences = _re.split(r'(?<=[.!?])\s+', text.strip())
    sentences = [s for s in sentences if len(s) > 20]
    if not sentences:
        return text[:300]
    words = _re.findall(r'\b[a-z]{4,}\b', text.lower())
    stop = set('that with this from have will your their about would could should these those'.split())
    freq = Counter(w for w in words if w not in stop)
    scored = sorted(sentences, key=lambda s: sum(freq.get(w,0) for w in _re.findall(r'\b[a-z]{4,}\b', s.lower())), reverse=True)
    top = scored[:max_points]
    # restore original order
    return "\n".join(s for s in sentences if s in top)

def tool_ai_summarize(params):
    text = (params.get("text") or params.get("url") or "").strip()
    if not text:
        return {"error": "text or url required"}
    if len(text) > 5000:
        text = text[:5000]
    q = "Summarize the following in 3-5 concise bullet points. Return only the bullets:\n\n%s" % text
    try:
        r = requests.post(POLLINATIONS_TXT, data=json.dumps({"messages": [{"role": "user", "content": q}]}),
                          timeout=45, headers={"Content-Type": "application/json"})
        if r.status_code == 200 and r.text.strip():
            return {"result": {"summary": r.text.strip(), "chars_in": len(text), "engine": "pollinations"}}
    except Exception:
        pass
    # fallback: local extractive summary
    return {"result": {"summary": _local_summarize(text), "chars_in": len(text), "engine": "local-extractive",
                       "note": "LLM unavailable; applied offline extractive summary."}}

# ---------- Translation ----------
def tool_translate(params):
    text = (params.get("text") or "").strip()
    if not text:
        return {"error": "text required"}
    src = params.get("from", "auto")
    tgt = params.get("to", "en")
    if len(text) > 3000:
        text = text[:3000]
    # try LibreTranslate public
    try:
        r = requests.post("https://libretranslate.com/translate",
                          data={"q": text, "source": src, "target": tgt, "format": "text"},
                          timeout=25)
        if r.status_code == 200 and "translatedText" in r.text:
            return {"result": {"translated": r.json()["translatedText"], "from": src, "to": tgt}}
    except Exception:
        pass
    # fallback mymemory
    r = _http_get("https://api.mymemory.translated.net/get?q=%s&langpair=%s|%s" %
                  (urllib.parse.quote(text), src, tgt), timeout=25)
    if r.status_code == 200:
        try:
            t = r.json()["responseData"]["translatedText"]
            return {"result": {"translated": t, "from": src, "to": tgt, "via": "mymemory"}}
        except Exception:
            pass
    return {"error": "translation failed"}

# ---------- Resume parser ----------
def tool_resume_parse(params):
    import pdfplumber
    src = params.get("pdf") or params.get("url") or ""
    raw = None
    if src.startswith("data:application/pdf"):
        raw = base64.b64decode(src.split(",", 1)[1])
    elif src.startswith("http"):
        raw = _http_get(src, timeout=30).content
    if not raw:
        return {"error": "pdf (data_url or url) required"}
    if len(raw) > 8 * 1024 * 1024:
        return {"error": "pdf too large (max 8MB)"}
    out = {"name": None, "email": None, "phone": None, "skills": [], "sections": {}}
    with pdfplumber.open(io.BytesIO(raw)) as pdf:
        txt = "\n".join((pg.extract_text() or "") for pg in pdf.pages)
    out["chars"] = len(txt)
    m = re.search(r"[\w.+-]+@[\w-]+\.[\w.-]+", txt)
    if m: out["email"] = m.group(0)
    m = re.search(r"(?:\+?\d[\d\s().-]{7,}\d)", txt)
    if m: out["phone"] = m.group(0).strip()
    # name heuristic: first non-empty short line
    for line in txt.splitlines():
        line = line.strip()
        if line and len(line) < 40 and not "@" in line:
            out["name"] = line; break
    skills_kw = ["python", "javascript", "typescript", "go", "rust", "react", "node",
                 "aws", "gcp", "docker", "kubernetes", "sql", "postgres", "linux",
                 "machine learning", "ai", "pytorch", "tensorflow", "fastapi", "graphql"]
    low = txt.lower()
    out["skills"] = [s for s in skills_kw if s in low]
    return {"result": out}

# ---------- PDF -> Word ----------
def tool_pdf_to_word(params):
    import pdfplumber
    from docx import Document
    src = params.get("pdf") or params.get("url") or ""
    raw = None
    if src.startswith("data:application/pdf"):
        raw = base64.b64decode(src.split(",", 1)[1])
    elif src.startswith("http"):
        raw = _http_get(src, timeout=30).content
    if not raw:
        return {"error": "pdf (data_url or url) required"}
    if len(raw) > 8 * 1024 * 1024:
        return {"error": "pdf too large (max 8MB)"}
    doc = Document()
    with pdfplumber.open(io.BytesIO(raw)) as pdf:
        for pg in pdf.pages:
            for line in (pg.extract_text() or "").splitlines():
                doc.add_paragraph(line)
    buf = io.BytesIO()
    doc.save(buf)
    return {"result": {"data_url": _b64(buf.getvalue(), "application/vnd.openxmlformats-officedocument.wordprocessingml.document"),
                       "format": "docx", "bytes": len(buf.getvalue())}}

# ---------- Plagiarism checker ----------
def tool_plagiarism(params):
    text = (params.get("text") or "").strip()
    if not text:
        return {"error": "text required"}
    snippet = " ".join(text.split()[:30])
    r = _http_get("https://www.google.com/search?q=%s" % urllib.parse.quote(snippet), timeout=25,
                  headers={"User-Agent": "Mozilla/5.0"})
    hits = len(re.findall(r"<a href=\"https://[^>]*\"", r.text))
    return {"result": {"query_snippet": snippet, "approx_indexed_pages": hits,
                       "note": "Higher page count = more likely the phrasing exists online. Heuristic only."}}

# ---------- QR code ----------
def tool_qr(params):
    import segno
    data = (params.get("data") or "").strip()
    if not data:
        return {"error": "data required"}
    if len(data) > 2000:
        return {"error": "data too long (max 2000)"}
    buf = io.BytesIO()
    segno.make(data, error='m').save(buf, kind='png', scale=8, border=2)
    return {"result": {"data_url": _b64(buf.getvalue(), "image/png"), "format": "png",
                       "bytes": len(buf.getvalue()), "data": data}}

# ---------- Link preview / unfurl ----------
def tool_link_preview(params):
    from bs4 import BeautifulSoup
    url = (params.get("url") or "").strip()
    if not url:
        return {"error": "url required"}
    try:
        r = _http_get(url, timeout=25)
        soup = BeautifulSoup(r.text, "html.parser")
        def meta(prop):
            tag = soup.find("meta", attrs={"property": prop}) or soup.find("meta", attrs={"name": prop})
            return tag.get("content") if tag else None
        title = meta("og:title") or (soup.title.string if soup.title else None)
        desc = meta("og:description") or meta("description")
        img = meta("og:image")
        site = meta("og:site_name")
        return {"result": {"url": url, "title": title, "description": desc,
                            "image": img, "site_name": site,
                            "note": "Open Graph unfurl card data."}}
    except Exception as e:
        return {"error": "preview failed: %s" % str(e)[:120]}

# ---------- PDF compress ----------
def tool_pdf_compress(params):
    import pypdf
    src = params.get("pdf") or params.get("url") or ""
    raw = None
    if src.startswith("data:application/pdf"):
        raw = base64.b64decode(src.split(",", 1)[1])
    elif src.startswith("http"):
        raw = _http_get(src, timeout=30).content
    if not raw:
        return {"error": "pdf (data_url or url) required"}
    if len(raw) > 12 * 1024 * 1024:
        return {"error": "pdf too large (max 12MB)"}
    try:
        reader = pypdf.PdfReader(io.BytesIO(raw))
        writer = pypdf.PdfWriter()
        for pg in reader.pages:
            writer.add_page(pg)
        buf = io.BytesIO()
        writer.write(buf)
        comp = buf.getvalue()
        return {"result": {"data_url": _b64(comp, "application/pdf"), "format": "pdf",
                           "bytes_in": len(raw), "bytes_out": len(comp),
                           "saved_pct": round(100 * (1 - len(comp) / len(raw)), 1)}}
    except Exception as e:
        return {"error": "compress failed: %s" % str(e)[:120]}

# ---------- Video thumbnail ----------
def tool_video_thumb(params):
    url = (params.get("url") or "").strip()
    if not url:
        return {"error": "url required"}
    t = int(params.get("at", 1))
    with tempfile.TemporaryDirectory() as td:
        out = os.path.join(td, "thumb.png")
        try:
            subprocess.run(["ffmpeg", "-y", "-i", url, "-ss", str(t), "-vframes", "1",
                            "-vf", "scale=480:-1", out], timeout=60,
                           capture_output=True, check=True)
        except Exception as e:
            return {"error": "thumb failed: %s" % str(e)[:120]}
        with open(out, "rb") as f:
            b = f.read()
    return {"result": {"data_url": _b64(b, "image/png"), "format": "png", "bytes": len(b),
                       "at_sec": t}}
