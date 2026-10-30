# -*- coding: utf-8 -*-
"""Remove Semantic Scholar records already found in Europe PMC (by DOI, PMID or normalised title), records typed as
reviews and records without an abstract. Writes search/s2_new.jsonl and search/s2_dedupe_log.json."""
import collections
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def norm(t):
    return re.sub(r'[^a-z0-9]', '', (t or '').lower())


ep = [json.loads(l) for l in open(ROOT / 'search' / 'records.jsonl', encoding='utf-8')]
dois = {(r.get('doi') or '').lower() for r in ep} - {''}
pmids = {str(r.get('pmid') or '') for r in ep} - {''}
titles = {norm(r.get('title')) for r in ep} - {''}
s2 = [json.loads(l) for l in open(ROOT / 'search' / 's2_records.jsonl', encoding='utf-8')]
log, new, seen = collections.Counter(), [], set()
for r in s2:
    if (r['doi'] and r['doi'] in dois) or (r['pmid'] and r['pmid'] in pmids) or norm(r['title']) in titles:
        log['in_europe_pmc'] += 1
    elif norm(r['title']) in seen:
        log['duplicate'] += 1
    elif 'Review' in r['types']:
        log['review_pubtype'] += 1
    elif len(r['abstract']) < 100:
        log['no_abstract'] += 1
    else:
        seen.add(norm(r['title'])); new.append(r); log['to_screen'] += 1
with open(ROOT / 'search' / 's2_new.jsonl', 'w', encoding='utf-8') as f:
    for r in new:
        f.write(json.dumps(r, ensure_ascii=False) + '\n')
log['hits'] = len(s2)
json.dump(dict(log), open(ROOT / 'search' / 's2_dedupe_log.json', 'w'), indent=1)
print(dict(log))
