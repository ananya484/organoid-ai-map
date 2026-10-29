"""Agreement of the third coder (Claude Opus 5.5) with the two Claude Sonnet 5.5 coders on the 60-record sample.

Writes results/three_coder_agreement.json.
"""
import collections, csv, glob, json, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, 'data')
VAL = ['none_reported', 'internal_split_or_cv', 'external_dataset', 'experimental_prospective', 'clinical_outcome']
C1 = {}
for f in glob.glob(os.path.join(D, 'extract_batch*.csv')):
    for r in csv.DictReader(open(f, encoding='utf-8')):
        C1[r['id']] = r
C2 = {r['id']: r for r in csv.DictReader(open(os.path.join(D, 'extract_qc_second_coder.csv'), encoding='utf-8'))}
C3 = {r['id']: r for r in csv.DictReader(open(os.path.join(D, 'extract_qc_third_coder.csv'), encoding='utf-8'))}
ids = [i for i in C3 if i in C1 and i in C2]


def kappa(a, b):
    n = len(a); po = sum(x == y for x, y in zip(a, b)) / n
    ca, cb = collections.Counter(a), collections.Counter(b)
    pe = sum(ca[k] * cb[k] for k in set(ca) | set(cb)) / n ** 2
    return round(100 * po, 1), round((po - pe) / (1 - pe), 2) if pe < 1 else 1.0


def fleiss(rows):
    """rows: list of category lists (one label per rater)."""
    cats = sorted({c for r in rows for c in r}); n = len(rows[0]); N = len(rows)
    P = [(sum(r.count(c) ** 2 for c in cats) - n) / (n * (n - 1)) for r in rows]
    pj = [sum(r.count(c) for r in rows) / (N * n) for c in cats]
    Pb = sum(P) / N; Pe = sum(p * p for p in pj)
    return round((Pb - Pe) / (1 - Pe), 2)


def hv(v):
    v = [x.strip() for x in (v or '').split(';') if x.strip() in VAL]
    return max(v, key=VAL.index) if v else 'none_reported'


inc = lambda C, i: C[i]['include'].strip().lower()
out = dict(n=len(ids))
for lab, C in (('sonnet1', C1), ('sonnet2', C2)):
    out[f'opus_vs_{lab}_include_pct'], out[f'opus_vs_{lab}_include_kappa'] = kappa([inc(C3, i) for i in ids], [inc(C, i) for i in ids])
    both = [i for i in ids if inc(C3, i) == 'yes' == inc(C, i)]
    out[f'opus_vs_{lab}_both_included'] = len(both)
    out[f'opus_vs_{lab}_validation_pct'], out[f'opus_vs_{lab}_validation_kappa'] = kappa([hv(C3[i]['validation']) for i in both], [hv(C[i]['validation']) for i in both])
out['fleiss_include_3coders'] = fleiss([[inc(C, i) for C in (C1, C2, C3)] for i in ids])
out['unanimous_include_pct'] = round(100 * sum(len({inc(C, i) for C in (C1, C2, C3)}) == 1 for i in ids) / len(ids), 1)
all3 = [i for i in ids if all(inc(C, i) == 'yes' for C in (C1, C2, C3))]
out['all3_included'] = len(all3)
out['fleiss_validation_3coders'] = fleiss([[hv(C[i]['validation']) for C in (C1, C2, C3)] for i in all3]) if all3 else None
out['opus_included'] = sum(inc(C3, i) == 'yes' for i in ids)
json.dump(out, open(os.path.join(ROOT, 'results', 'three_coder_agreement.json'), 'w'), indent=1)
print(json.dumps(out, indent=1))
