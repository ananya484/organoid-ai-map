# -*- coding: utf-8 -*-
"""Supplementary Semantic Scholar search: merge the screening batches, remove records that duplicate studies already
in the Europe PMC map, classify by publication type and compare the coded profile with the main map.
Writes data/s2_included.csv and results/s2_supplement.json. Run after search_s2.py, dedupe_s2.py and analyse.py."""
import collections
import csv
import glob
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VAL = ['none_reported', 'internal_split_or_cv', 'external_dataset', 'experimental_prospective', 'clinical_outcome']
BEYOND = set(VAL[2:])


def highest(v):
    lv = [x.strip() for x in v.split(';') if x.strip() in VAL]
    return max(lv, key=VAL.index) if lv else 'none_reported'
# included records that are another version (meeting abstract, arXiv or bioRxiv) of a study already in the map,
# identified by title overlap and first author and checked by hand
SAME_AS_MAP = {'S2:362b00c1a', 'S2:87aac412e', 'S2:b116a7163', 'S2:be042a524', 'S2:a9b60b305', 'S2:942446a4b',
               'S2:8d54519a'}
SAME_AS_S2 = {'S2:192633811'}          # second meeting abstract of S2:5dfcba0d6

rows = []
for f in sorted(glob.glob(str(ROOT / 'data' / 'extract_s2_batch*.csv'))):
    rows += list(csv.DictReader(open(f, encoding='utf-8')))
s2 = {json.loads(l)['id']: json.loads(l) for l in open(ROOT / 'search' / 's2_new.jsonl', encoding='utf-8')}
dlog = json.load(open(ROOT / 'search' / 's2_dedupe_log.json'))
# re-check of every record coded as compared with in vivo outcomes (log: data/s2_recheck_log.csv)
RECHECK = {'S2:e3eafd6f': dict(human_relevance_benchmark='none'), 'S2:199bc490': dict(human_relevance_benchmark='none'),
           'S2:a42c7fbe': dict(human_relevance_benchmark='clinical', validation='clinical_outcome'),
           'S2:739402d8': dict(include='no', exclude_reason='other'), 'S2:8d736b39': dict(human_relevance_benchmark='none')}
for r in rows:
    for p, ch in RECHECK.items():
        if r['id'].startswith(p):
            r.update(ch)
inc_all = [r for r in rows if r['include'].strip().lower() == 'yes']


def drop(r):
    return any(r['id'].startswith(p) for p in SAME_AS_MAP | SAME_AS_S2)


inc = [r for r in inc_all if not drop(r)]


def kind(x):
    t, v = x['title'], (x['journal'] or '')
    if re.match(r'^(Abstract\b|\d+\W)', t) or re.search(r'\bAbstract [A-Z]{0,3}[\d-]+:', t):
        return 'meeting_abstract'
    if 'arxiv' in v.lower():
        return 'arxiv'
    if re.search(r'proceedings|conference|symposium|workshop|congress', v, re.I) or 'IEEE International' in v:
        return 'conference_paper'
    if re.search(r'biorxiv|medrxiv|research square|ssrn|preprint', v, re.I):
        return 'preprint'
    return 'journal_article'


S = dict(hits=dlog['hits'], in_europe_pmc=dlog['in_europe_pmc'], review_pubtype=dlog['review_pubtype'],
         no_abstract=dlog['no_abstract'], screened=len(rows), included_raw=len(inc_all),
         same_as_map=sum(1 for r in inc_all if any(r['id'].startswith(p) for p in SAME_AS_MAP)),
         same_as_s2=sum(1 for r in inc_all if any(r['id'].startswith(p) for p in SAME_AS_S2)), new_studies=len(inc))
S['excluded'] = dict(collections.Counter(r['exclude_reason'] for r in rows if r['include'].strip().lower() != 'yes'))
K = collections.Counter(kind(s2[r['id']]) for r in inc)
S['kind'] = dict(K)
S['peer_reviewed_full'] = K['journal_article'] + K['conference_paper']
n = len(inc)
S['chip'] = sum(r['system'] in ('organ_on_chip', 'organoid_on_chip', 'multiple') for r in inc)
S['pct_chip'] = round(100 * S['chip'] / n, 1)
S['tox'] = sum('toxicity_safety' in r['application'] for r in inc)
S['pct_tox'] = round(100 * S['tox'] / n, 1)
S['none'] = sum(highest(r['validation']) == 'none_reported' for r in inc)
S['pct_none'] = round(100 * S['none'] / n, 1)
S['beyond'] = sum(highest(r['validation']) in BEYOND for r in inc)
S['pct_beyond'] = round(100 * S['beyond'] / n, 1)
S['in_vivo'] = sum(r['human_relevance_benchmark'] not in ('none', '') for r in inc)
S['animal'] = sum(r['human_relevance_benchmark'] in ('animal', 'both') for r in inc)
S['pct_in_vivo'] = round(100 * S['in_vivo'] / n, 1)
S['regulatory'] = sum(r['regulatory_mention'] == 'yes' for r in inc)
main = json.load(open(ROOT / 'results' / 'summary.json'))
S['combined_n'] = main['included'] + n
S['combined_beyond'] = main['n_beyond_internal'] + S['beyond']
S['combined_pct_beyond'] = round(100 * S['combined_beyond'] / S['combined_n'], 1)
S['pct_of_combined_new'] = round(100 * n / S['combined_n'], 1)
json.dump(S, open(ROOT / 'results' / 's2_supplement.json', 'w'), indent=1)
with open(ROOT / 'data' / 's2_included.csv', 'w', newline='', encoding='utf-8') as fh:
    w = csv.writer(fh)
    keys = ['id', 'year', 'first_author', 'title', 'journal', 'doi', 'kind'] + [k for k in rows[0] if k not in ('id', 'include', 'exclude_reason')]
    w.writerow(keys)
    for r in inc:
        x = s2[r['id']]
        w.writerow([r['id'], x['year'], x['first_author'], x['title'], x['journal'], x['doi'], kind(x)] + [r[k] for k in keys[7:]])
print(json.dumps(S, indent=1))
