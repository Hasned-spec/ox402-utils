"""x402_tools17.py — High-demand agent utilities (secure, no external auth, CPU-only)."""

import io, json, re, base64, urllib.parse, subprocess, tempfile, os, hashlib, time
import requests
from urllib.request import urlopen

# ---------- OpenAPI/Swagger fetcher ----------
def tool_openapi_fetch(params):
    """Fetch and parse OpenAPI/Swagger spec from a URL. Returns normalized spec + endpoint summary."""
    url = (params.get('url') or '').strip()
    if not url:
        return {'error': 'url required'}
    try:
        r = requests.get(url, timeout=20, headers={'User-Agent': 'ox402/1.0'})
        if r.status_code != 200:
            return {'error': f'fetch failed: {r.status_code}'}
        spec = r.json() if r.headers.get('content-type','').startswith('application/json') else r.text
        if isinstance(spec, str):
            spec = json.loads(spec)
        paths = spec.get('paths', {})
        endpoints = []
        for path, methods in paths.items():
            for method, details in methods.items():
                if method.lower() in ('get','post','put','patch','delete','head','options'):
                    endpoints.append({
                        'method': method.upper(),
                        'path': path,
                        'summary': details.get('summary',''),
                        'operationId': details.get('operationId',''),
                        'parameters': [p.get('name','') for p in details.get('parameters',[])],
                        'security': details.get('security', spec.get('security', [])),
                    })
        return {
            'info': spec.get('info', {}),
            'servers': spec.get('servers', []),
            'endpoint_count': len(endpoints),
            'endpoints': endpoints[:50],
            'security_schemes': list(spec.get('components',{}).get('securitySchemes',{}).keys()),
            'note': 'Full spec available in original; this is a summary for agent context.'
        }
    except Exception as e:
        return {'error': f'parse failed: {str(e)[:200]}'}

# ---------- GraphQL introspection + query ----------
def tool_graphql(params):
    """Introspect a GraphQL endpoint or execute a query. Pass introspect=true for schema, or query+variables to run."""
    url = (params.get('url') or '').strip()
    if not url:
        return {'error': 'url required'}
    headers = {'Content-Type': 'application/json', 'User-Agent': 'ox402/1.0'}
    auth = params.get('authorization')
    if auth:
        headers['Authorization'] = auth
    
    if params.get('introspect'):
        query = '''
        query IntrospectionQuery {
          __schema {
            queryType { name }
            mutationType { name }
            subscriptionType { name }
            types { name kind description fields { name description type { name kind ofType { name kind } } } }
            directives { name description locations args { name description type { name kind ofType { name kind } } } }
          }
        }'''
        payload = {'query': query}
    else:
        query = params.get('query')
        if not query:
            return {'error': 'query or introspect=true required'}
        payload = {'query': query, 'variables': params.get('variables', {})}
    
    try:
        r = requests.post(url, json=payload, headers=headers, timeout=30)
        if r.status_code != 200:
            return {'error': f'GraphQL error: {r.status_code} {r.text[:200]}'}
        data = r.json()
        if params.get('introspect'):
            schema = data.get('data', {}).get('__schema', {})
            if not schema:
                return {'error': 'introspection failed: no __schema in response', 'raw': data}
            types = [t for t in schema.get('types', []) if not t['name'].startswith('__')]
            return {
                'query_type': schema.get('queryType', {}).get('name'),
                'mutation_type': schema.get('mutationType', {}).get('name'),
                'type_count': len(types),
                'types': [{'name': t['name'], 'kind': t['kind'], 'fields': len(t.get('fields', []))} for t in types[:100]],
                'directives': [d['name'] for d in schema.get('directives', [])],
            }
        return data
    except Exception as e:
        return {'error': f'GraphQL failed: {str(e)[:200]}'}

# ---------- SQLite sandbox (read-only by default) ----------
def tool_sqlite(params):
    """Run a SQL query on an in-memory SQLite DB. Pass sql and optionally csv_data (list of {table, csv_text}) to load data first. Read-only by default; set allow_write=true for DML (still isolated)."""
    import sqlite3
    sql = (params.get('sql') or '').strip()
    if not sql:
        return {'error': 'sql required'}
    allow_write = params.get('allow_write', False)
    
    conn = sqlite3.connect(':memory:')
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    
    for item in params.get('csv_data', []):
        table = item.get('table')
        csv_text = item.get('csv_text')
        if not table or not csv_text:
            continue
        import csv
        from io import StringIO
        reader = csv.DictReader(StringIO(csv_text))
        rows = list(reader)
        if not rows:
            continue
        cols = rows[0].keys()
        cur.execute(f'CREATE TABLE {table} ({", ".join(f"{c} TEXT" for c in cols)})')
        for row in rows:
            vals = [row.get(c, '') for c in cols]
            cur.execute(f'INSERT INTO {table} VALUES ({", ".join("?" for _ in cols)})', vals)
        conn.commit()
    
    if not allow_write:
        blocked = ['INSERT', 'UPDATE', 'DELETE', 'DROP', 'ALTER', 'CREATE', 'ATTACH', 'DETACH', 'PRAGMA', 'VACUUM']
        if any(sql.upper().strip().startswith(b) for b in blocked):
            return {'error': 'write operations require allow_write=true (still sandboxed)'}
    
    try:
        cur.execute(sql)
        if sql.strip().upper().startswith('SELECT'):
            rows = [dict(r) for r in cur.fetchall()]
            return {'rows': rows, 'count': len(rows), 'columns': [d[0] for d in cur.description] if cur.description else []}
        else:
            conn.commit()
            return {'affected': cur.rowcount, 'last_id': cur.lastrowid}
    except Exception as e:
        return {'error': f'SQL error: {str(e)[:200]}'}
    finally:
        conn.close()

# ---------- Embedding / vector search (local, fastembed) ----------
def tool_embed(params):
    """Generate embeddings for text(s) using local fastembed (BAAI/bge-small-en-v1.5). Returns vectors + optional similarity search against provided docs."""
    from fastembed import TextEmbedding
    texts = params.get('texts') or [params.get('text', '')]
    if not texts or not any(texts):
        return {'error': 'texts or text required'}
    if isinstance(texts, str):
        texts = [texts]
    texts = texts[:50]
    
    model = TextEmbedding(model_name='BAAI/bge-small-en-v1.5')
    vectors = list(model.embed(texts))
    
    docs = params.get('docs')
    if docs:
        doc_texts = [d.get('text','') for d in docs]
        doc_vecs = list(model.embed(doc_texts))
        import numpy as np
        qv = np.array(vectors[0])
        dv = np.array(doc_vecs)
        sims = (dv @ qv) / (np.linalg.norm(dv, axis=1) * np.linalg.norm(qv) + 1e-8)
        ranked = sorted(zip(docs, sims), key=lambda x: x[1], reverse=True)[:params.get('top_k', 10)]
        return {
            'query_vector': vectors[0],
            'matches': [{'id': d.get('id'), 'text': d.get('text')[:200], 'score': float(s)} for d, s in ranked]
        }
    
    return {'vectors': vectors, 'dim': len(vectors[0]) if vectors else 0}

# ---------- Pricing estimator (helps agents budget) ----------
def tool_price_estimate(params):
    """Estimate cost for a batch of tool calls. Pass calls: [{tool, count}] or {tool: count}. Returns USD total + per-tool breakdown."""
    from x402_server import TOOLS
    calls = params.get('calls', {})
    if isinstance(calls, list):
        calls = {c['tool']: c.get('count', 1) for c in calls}
    if not calls:
        return {'error': 'calls required'}
    
    total = 0.0
    breakdown = {}
    for tool, count in calls.items():
        if tool not in TOOLS:
            breakdown[tool] = {'error': 'unknown tool'}
            continue
        price = TOOLS[tool][1]
        tier = TOOLS[tool][2]
        cost = price * count
        breakdown[tool] = {'price_per_call': price, 'tier': tier, 'count': count, 'cost_usd': round(cost, 4)}
        total += cost
    
    free_calls = params.get('free_trial_remaining', 10)
    free_applied = {}
    remaining_free = free_calls
    for tool, info in breakdown.items():
        if info.get('tier') == 'free' and remaining_free > 0:
            free_here = min(info['count'], remaining_free)
            info['free_calls'] = free_here
            info['cost_usd'] = round(info['price_per_call'] * (info['count'] - free_here), 4)
            remaining_free -= free_here
            free_applied[tool] = free_here
    
    total_after_free = sum(b.get('cost_usd', 0) for b in breakdown.values())
    return {
        'total_usd': round(total_after_free, 4),
        'breakdown': breakdown,
        'free_trial_applied': free_applied,
        'free_remaining': remaining_free,
        'note': 'Free trial: 10 calls/IP on tier=free tools. Use this to budget before paying.'
    }

# ---------- API test / dry-run (simulate x402 call without payment) ----------
def tool_dry_run(params):
    """Simulate a tool call WITHOUT payment — returns the 402 challenge structure and estimated cost. Use to preview before paying."""
    from x402_server import TOOLS, price_for
    tool = params.get('tool')
    if not tool or tool not in TOOLS:
        return {'error': f'unknown tool: {tool}'}
    
    fn, price, tier, desc, sample = TOOLS[tool]
    return {
        'tool': tool,
        'price_usd': price,
        'tier': tier,
        'description': desc,
        'sample_input': sample,
        'challenge_preview': {
            'x402Version': 1,
            'error': 'X402_PAYMENT_REQUIRED',
            'accepts': [{
                'scheme': 'exact',
                'network': 'eip155:8453',
                'maxAmountRequired': f'{price:.4f}'.rstrip('0').rstrip('.'),
                'resource': '/x402/paid/' + tool,
                'description': 'ox402 utility call: ' + desc,
                'payTo': '0xE9C9cC258f7137fD0AbA4Ae513F0Cfa288c0cDc9',
                'asset': '0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913',
            }],
            'free_trial': {'calls_per_ip': 10, 'tier': tier}
        }
    }

# ---------- Batch caller (agent convenience: multiple tools, one payment flow) ----------
def tool_batch(params):
    """Execute multiple tools in sequence with a single x402 payment (sum of prices). Pass calls: [{tool, input}]. Returns aggregated results."""
    from x402_server import TOOLS
    calls = params.get('calls', [])
    if not calls:
        return {'error': 'calls list required'}
    if len(calls) > 10:
        return {'error': 'max 10 calls per batch'}
    
    results = []
    total_price = 0.0
    for item in calls:
        tool = item.get('tool')
        inp = item.get('input', {})
        if tool not in TOOLS:
            results.append({'tool': tool, 'error': 'unknown tool'})
            continue
        fn, price, tier, desc, _ = TOOLS[tool]
        total_price += price
        try:
            out = fn(inp)
            results.append({'tool': tool, 'result': out})
        except Exception as e:
            results.append({'tool': tool, 'error': str(e)[:200]})
    
    return {
        'total_price_usd': round(total_price, 4),
        'call_count': len(calls),
        'results': results,
        'note': 'Batch executed. Single x402 payment for sum of prices would be required on /paid/batch.'
    }