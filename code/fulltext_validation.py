# -*- coding: utf-8 -*-
"""Full-text validation coding of the open-access included studies.
Reads data/fulltext_packets/coded_batch{1-6}.csv (main coder) and coded_qc30_second.csv (second coder, different model),
compares full-text with abstract-level validation, and writes results/fulltext_validation.json and
data/fulltext_validation.csv. Run after fulltext_code_check.py."""
import collections
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
P = ROOT / 'data' / 'fulltext_packets'
LEVELS = ['none_reported', 'internal_split_or_cv', 'external_dataset', 'experimental_prospective', 'clinical_outcome']
BEYOND = set(LEVELS[2:])

ab = {r['pmcid']: r for r in csv.DictReader(open(ROOT / 'results' / 'fulltext_code_check.csv', encoding='utf-8'))}
ft = {}
for b in range(1, 7):
    for r in csv.DictReader(open(P / f'coded_batch{b}.csv', encoding='utf-8')):
        ft[r['pmcid'].strip()] = r
assert set(ft) == set(ab), (len(ft), len(ab), set(ab) - set(ft), set(ft) - set(ab))
for r in ft.values():
    assert r['validation_ft'] in LEVELS, r


def kappa(a, b):
    n = len(a); po = sum(x == y for x, y in zip(a, b)) / n
    ca, cb = collections.Counter(a), collections.Counter(b)
    pe = sum(ca[k] * cb[k] for k in set(ca) | set(cb)) / n ** 2
    return round(100 * po, 1), round((po - pe) / (1 - pe), 2) if pe < 1 else 1.0


n = len(ft)
S = dict(ftv_n=n)
for lv in LEVELS:
    S[f'ftv_{lv}'] = sum(r['validation_ft'] == lv for r in ft.values())
    S[f'ftv_abs_{lv}'] = sum(ab[i]['abstract_validation'] == lv for i in ft)
S['ftv_beyond'] = sum(r['validation_ft'] in BEYOND for r in ft.values())
S['ftv_abs_beyond'] = sum(ab[i]['abstract_validation'] in BEYOND for i in ft)
S['ftv_pct_beyond'] = round(100 * S['ftv_beyond'] / n, 1)
S['ftv_abs_pct_beyond'] = round(100 * S['ftv_abs_beyond'] / n, 1)
S['ftv_pct_none'] = round(100 * S['ftv_none_reported'] / n, 1)
S['ftv_abs_pct_none'] = round(100 * S['ftv_abs_none_reported'] / n, 1)
rank = {lv: i for i, lv in enumerate(LEVELS)}
S['ftv_higher_than_abstract'] = sum(rank[ft[i]['validation_ft']] > rank[ab[i]['abstract_validation']] for i in ft)
S['ftv_lower_than_abstract'] = sum(rank[ft[i]['validation_ft']] < rank[ab[i]['abstract_validation']] for i in ft)
S['ftv_same_as_abstract'] = n - S['ftv_higher_than_abstract'] - S['ftv_lower_than_abstract']
S['ftv_pct_same_as_abstract'] = round(100 * S['ftv_same_as_abstract'] / n, 1)
S['ftv_abs_vs_ft_agree'], S['ftv_abs_vs_ft_kappa'] = kappa([ab[i]['abstract_validation'] for i in ft], [ft[i]['validation_ft'] for i in ft])
S['ftv_in_vivo'] = sum(r['human_relevance_benchmark_ft'] != 'none' for r in ft.values())
S['ftv_animal'] = sum(r['human_relevance_benchmark_ft'] in ('animal', 'both') for r in ft.values())
S['ftv_pct_in_vivo'] = round(100 * S['ftv_in_vivo'] / n, 1)
for u in ['donor_or_patient', 'batch_or_lab', 'compound', 'image_or_organoid_only', 'unclear']:
    S[f'ftv_unit_{u}'] = sum(r['unit_independence'] == u for r in ft.values())
S['ftv_unit_independent'] = S['ftv_unit_donor_or_patient'] + S['ftv_unit_batch_or_lab'] + S['ftv_unit_compound']
S['ftv_pct_unit_independent'] = round(100 * S['ftv_unit_independent'] / n, 1)

q = {r['pmcid'].strip(): r for r in csv.DictReader(open(P / 'coded_qc30_second.csv', encoding='utf-8'))}
ids = sorted(i for i in q if i in ft)
S['ftv_qc_n'] = len(ids)
S['ftv_qc_agree'], S['ftv_qc_kappa'] = kappa([ft[i]['validation_ft'] for i in ids], [q[i]['validation_ft'] for i in ids])
S['ftv_qc_beyond_agree'], S['ftv_qc_beyond_kappa'] = kappa([ft[i]['validation_ft'] in BEYOND for i in ids],
                                                           [q[i]['validation_ft'] in BEYOND for i in ids])
json.dump(S, open(ROOT / 'results' / 'fulltext_validation.json', 'w'), indent=1)
with open(ROOT / 'data' / 'fulltext_validation.csv', 'w', newline='', encoding='utf-8') as fh:
    w = csv.writer(fh)
    w.writerow(['pmcid', 'first_author', 'year', 'abstract_validation', 'validation_ft', 'human_relevance_benchmark_ft',
                'unit_independence', 'ft_notes', 'second_coder_validation_ft'])
    for i in sorted(ft):
        r = ft[i]
        w.writerow([i, ab[i]['first_author'], ab[i]['year'], ab[i]['abstract_validation'], r['validation_ft'],
                    r['human_relevance_benchmark_ft'], r['unit_independence'], r['ft_notes'], q.get(i, {}).get('validation_ft', '')])
print(json.dumps(S, indent=1))
