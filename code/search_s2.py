# -*- coding: utf-8 -*-
"""Supplementary search: the same query in Semantic Scholar (bulk search API; covers engineering venues such as
IEEE, ACS and RSC). Writes search/s2_records.jsonl and search/s2_log.json."""
import datetime
import json
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
QUERY = ('(organoid | organoids | "organ-on-a-chip" | "organ-on-chip" | "organs-on-chips" | "organs-on-a-chip" | '
         '"microphysiological system" | "microphysiological systems" | "tissue chip" | "tissue chips") + '
         '("machine learning" | "deep learning" | "artificial intelligence" | "neural network" | "neural networks" | '
         'convolutional | "random forest" | transformer | transformers | "computer vision")')
FIELDS = 'title,year,externalIds,publicationTypes,venue,abstract,authors'


def get(params):
    url = 'https://api.semanticscholar.org/graph/v1/paper/search/bulk?' + urllib.parse.urlencode(params)
    for attempt in range(8):
        try:
            return json.load(urllib.request.urlopen(url, timeout=120))
        except urllib.error.HTTPError as e:
            if e.code != 429:
                raise
            time.sleep(15 * (attempt + 1))     # shared unauthenticated rate limit
    raise RuntimeError('rate limited')


out, token = [], None
while True:
    p = dict(query=QUERY, year='2015-2026', fields=FIELDS)
    if token:
        p['token'] = token
    r = get(p)
    for w in r.get('data', []):
        ids = w.get('externalIds') or {}
        out.append(dict(id='S2:' + w['paperId'], doi=(ids.get('DOI') or '').lower(), pmid=str(ids.get('PubMed') or ''),
                        title=w.get('title') or '', year=w.get('year'), types=w.get('publicationTypes') or [],
                        journal=w.get('venue') or '', first_author=((w.get('authors') or [{}])[0].get('name') or ''),
                        abstract=w.get('abstract') or ''))
    token = r.get('token')
    if not token:
        break
    time.sleep(5)
with open(ROOT / 'search' / 's2_records.jsonl', 'w', encoding='utf-8') as f:
    for o in out:
        f.write(json.dumps(o, ensure_ascii=False) + '\n')
json.dump(dict(database='Semantic Scholar bulk search API', query=QUERY, years='2015-2026',
               date=datetime.date.today().isoformat(), hits=len(out), total_reported=r.get('total')),
          open(ROOT / 'search' / 's2_log.json', 'w'), indent=1)
print('hits', len(out))
