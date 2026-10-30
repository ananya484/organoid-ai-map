# -*- coding: utf-8 -*-
"""Flatten every results/*.json into results/numbers.json (file.key = value) for audit_numbers.py."""
import json
from pathlib import Path

RES = Path(__file__).resolve().parent.parent / 'results'
out = json.loads((RES / 'numbers.json').read_text()) if (RES / 'numbers.json').exists() else {}


def flat(prefix, v):
    if isinstance(v, dict):
        for k, x in v.items():
            flat(f'{prefix}.{k}', x)
    elif isinstance(v, (int, float)) and not isinstance(v, bool):
        out[prefix] = float(v)


for f in sorted(RES.glob('*.json')):
    if f.name != 'numbers.json':
        flat(f.stem, json.loads(f.read_text()))
(RES / 'numbers.json').write_text(json.dumps(out, indent=0))
print(len(out), 'numbers')
