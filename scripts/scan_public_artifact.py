#!/usr/bin/env python3
"""Scan every APK entry and container, or every public file. Never print values."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import zipfile

PATTERNS = {
    'unix_home': b'/' + b'home' + b'/',
    'mac_home': b'/' + b'Users' + b'/',
    'private_workspace': re.escape(bytes([46]) + b'hermes'),
    'private_key': rb'-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----',
    'github_token': rb'\b(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{40,})',
    'aws_key': rb'\b(?:AKIA|ASIA)[A-Z0-9]{16}\b',
    'google_api_key': rb'\bAIza[A-Za-z0-9_-]{35}\b',
    'slack_token': rb'\bxox[baprs]-[A-Za-z0-9-]{20,}',
    'credential_assignment': rb'(?i)\b(?:password|passwd|api[_-]?key|access[_-]?token|client[_-]?secret)\s*[:=]\s*[\x22\x27][A-Za-z0-9_+/=-]{12,}[\x22\x27]',
}

def scan(data):
    hits = {}
    for name, pattern in PATTERNS.items():
        count = len(re.findall(pattern, data))
        # Inspect UTF-16 strings too, without changing artifact bytes.
        count += len(re.findall(pattern, data.replace(b'\x00', b''))) if b'\x00' in data else 0
        if count:
            hits[name] = count
    return hits


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('target', type=Path)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    records = []
    if a.target.is_dir():
        items = [(str(f.relative_to(a.target)), f.read_bytes()) for f in sorted(a.target.rglob('*')) if f.is_file()]
    else:
        items = [('APK_CONTAINER', a.target.read_bytes())]
        with zipfile.ZipFile(a.target) as z:
            assert z.testzip() is None
            items += [(info.filename, z.read(info)) for info in z.infolist() if not info.is_dir()]
    for name, data in items:
        records.append({'entry': name, 'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest(), 'hits': scan(data)})
    result = {'status': 'FAIL' if any(r['hits'] for r in records) else 'PASS',
              'checked_entries': len(records), 'checked_bytes': sum(r['bytes'] for r in records),
              'patterns': list(PATTERNS), 'entries': records,
              'scope': 'complete raw bytes plus every decompressed entry; credential heuristics are not proof of absence of every possible secret'}
    a.output.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({k: v for k, v in result.items() if k != 'entries'}))
    for r in records:
        if r['hits']:
            print(json.dumps({'entry': r['entry'], 'hits': r['hits']}))
    raise SystemExit(result['status'] != 'PASS')

if __name__ == '__main__':
    main()
