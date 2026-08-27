FROM python:3.12-slim

WORKDIR /app

# System deps for tools: ffmpeg, poppler, tesseract, yt-dlp, etc.
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    poppler-utils \
    tesseract-ocr \
    tesseract-ocr-eng \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY x402_server.py x402_tools.py x402_tools2.py x402_tools3.py x402_tools4.py x402_tools5.py x402_tools6.py x402_tools7.py x402_tools8.py x402_tools9.py x402_tools10.py x402_tools11.py x402_tools12.py x402_tools13.py x402_tools14.py x402_tools15.py x402_tools16.py x402_security.py mcp_server.py ./

# Environment
ENV OX402_MCP_PORT=8796
ENV OX402_PORT=8793
ENV OX402_FACILITATOR=http://host.docker.internal:8090
ENV OX402_PAYTO=0xE9C9cC258f7137fD0AbA4Ae513F0Cfa288c0cDc9

EXPOSE 8796 8793

# Run MCP server (the x402 seller runs separately on host)
CMD ["python3", "mcp_server.py"]