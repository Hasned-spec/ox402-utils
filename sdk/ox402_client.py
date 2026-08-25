"""ox402 client: use 45 micro-priced utilities from any Python/LangChain agent.

pip install requests
    from ox402_client import ox402
    ox402.pay = my_x402_payer          # callable(challenge: dict) -> payment header str
    print(ox402.call('whois', {'domain': 'github.com'}))

Payment: each call returns HTTP 402 with a PAYMENT-REQUIRED challenge (x402, USDC on Base).
Set ox402.pay to a function that pays it (CDP wallet, privy, custom signer) and the client
retries automatically with the X-Payment header.
"""
import json

import requests

BASE = 'https://tracy-collar-preview-demands.trycloudflare.com/x402/paid'
MCP_URL = 'https://tracy-collar-preview-demands.trycloudflare.com/mcp402/'
TIMEOUT = 60


class Ox402Error(RuntimeError):
    pass


def call(tool: str, args: dict | None = None, pay=None):
    """Call a tool. On 402, invokes pay(challenge_dict)->header value, then retries once."""
    args = args or {}
    r = requests.post(f'{BASE}/{tool}', json=args, timeout=TIMEOUT)
    if r.status_code == 200:
        return r.json()
    if r.status_code == 402:
        if pay is None:
            pay = getattr(ox402, 'pay', None)
        if pay is None:
            raise Ox402Error('payment required; set ox402.pay(challenge)->payment_header')
        chal_b64 = r.headers.get('PAYMENT-REQUIRED') or ''
        import base64
        chal = json.loads(base64.b64decode(chal_b64)) if chal_b64 else {}
        header = pay(chal)
        r2 = requests.post(f'{BASE}/{tool}', json=args, timeout=TIMEOUT,
                           headers={'X-Payment': header})
        if r2.status_code == 200:
            return r2.json()
        raise Ox402Error(f'paid retry failed: {r2.status_code} {r2.text[:300]}')
    raise Ox402Error(f'{r.status_code}: {r.text[:300]}')


def catalog():
    """Free: full tool list with prices + schemas."""
    r = requests.get(BASE.rsplit('/paid', 1)[0] + '/', timeout=30)
    return r.json()


# ---- LangChain adapter -----------------------------------------------------
def langchain_tools(pay=None, names=None):
    """Return LangChain Tool objects for (optionally filtered) ox402 tools."""
    try:
        from langchain_core.tools import StructuredTool
    except ImportError:
        try:
            from langchain.tools import StructuredTool
        except ImportError as e:
            raise Ox402Error('pip install langchain') from e

    cat = catalog().get('tools', {})
    out = []
    for name, meta in cat.items():
        if names and name not in names:
            continue
        price = meta.get('price', 0)

        def _mk(n=price, tool_name=name):
            def run(**kw):
                res = call(tool_name, kw, pay=pay)
                return json.dumps(res, default=str)
            return run

        out.append(StructuredTool.from_function(
            func=_mk(),
            name=f'ox402_{name}',
            description=f"{meta.get('desc', name)} (costs ${price}/call, x402 USDC Base)",
        ))
    return out


class ox402:
    pay = None
    call = staticmethod(call)
    catalog = staticmethod(catalog)
    langchain_tools = staticmethod(langchain_tools)


if __name__ == '__main__':
    cat = catalog()
    tools = cat.get('tools', {})
    print(f'{len(tools)} tools; sample:')
    for n in list(tools)[:8]:
        print(' ', n, f"${tools[n]['price']}")
