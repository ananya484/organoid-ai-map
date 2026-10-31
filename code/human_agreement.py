"""Agreement between the author's human coding and the two AI coders. Reads data/human_coding.csv (exported by
data/human_coding.html) or, failing that, data/human_coding_60.xlsx.

Writes results/human_agreement.json.  Run after the author has filled the sheet.
"""
import collections, csv, glob, json, os
from openpyxl import load_workbook

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VAL = ['none_reported', 'internal_split_or_cv', 'external_dataset', 'experimental_prospective', 'clinical_outcome']
H = {}
CSV = os.path.join(ROOT, 'data', 'human_coding.csv')
if os.path.exists(CSV):
    for r in csv.DictReader(open(CSV, encoding='utf-8')):
        H[r['id']] = dict(include=r['include'].strip().lower(), application=r['application'].strip(), validation=r['validation'].strip())
else:
    ws = load_workbook(os.path.join(ROOT, 'data', 'human_coding_60.xlsx'))['code_me']
    for row in ws.iter_rows(min_row=2, values_only=True):
        if row[0] and row[3]:
            H[str(row[0])] = dict(include=str(row[3]).strip().lower(), application=(row[5] or '').strip(), validation=(row[6] or '').strip())
A1 = {}
for f in glob.glob(os.path.join(ROOT, 'data', 'extract_batch*.csv')):
    for r in csv.DictReader(open(f, encoding='utf-8')):
        A1[r['id']] = r
A2 = {r['id']: r for r in csv.DictReader(open(os.path.join(ROOT, 'data', 'extract_qc_second_coder.csv'), encoding='utf-8'))}
A3 = {r['id']: r for r in csv.DictReader(open(os.path.join(ROOT, 'data', 'extract_qc_third_coder.csv'), encoding='utf-8'))}


def kappa(a, b):
    n = len(a); po = sum(x == y for x, y in zip(a, b)) / n
    ca, cb = collections.Counter(a), collections.Counter(b)
    pe = sum(ca[k] * cb[k] for k in set(ca) | set(cb)) / n ** 2
    return round(100 * po, 1), round((po - pe) / (1 - pe), 2) if pe < 1 else 1.0


def hv(v):
    v = [x.strip() for x in (v or '').split(';') if x.strip() in VAL]
    return max(v, key=VAL.index) if v else 'none_reported'


out = {'human_n': len(H)}
for lab, A in (('ai1', A1), ('ai2', A2), ('ai3', A3)):
    ids = [i for i in H if i in A]
    out[f'human_vs_{lab}_include_agreement_pct'], out[f'human_vs_{lab}_include_kappa'] = kappa(
        [H[i]['include'] for i in ids], [A[i]['include'].strip().lower() for i in ids])
    both = [i for i in ids if H[i]['include'] == 'yes' == A[i]['include'].strip().lower()]
    out[f'human_vs_{lab}_both_included'] = len(both)
    if both:
        out[f'human_vs_{lab}_validation_agreement_pct'], out[f'human_vs_{lab}_validation_kappa'] = kappa(
            [H[i]['validation'] or 'none_reported' for i in both], [hv(A[i]['validation']) for i in both])
        out[f'human_vs_{lab}_application_match_pct'] = round(100 * sum(
            H[i]['application'] in [x.strip() for x in A[i]['application'].split(';')] for i in both) / len(both), 1)
# Fleiss' kappa for inclusion across the human and all three AI coders
def fleiss(rows):
    cats = sorted({c for r in rows for c in r}); n = len(rows[0]); N = len(rows)
    P = [(sum(r.count(c) ** 2 for c in cats) - n) / (n * (n - 1)) for r in rows]
    pj = [sum(r.count(c) for r in rows) / (N * n) for c in cats]
    Pb, Pe = sum(P) / N, sum(p * p for p in pj)
    return round((Pb - Pe) / (1 - Pe), 2)


ids = [i for i in H if i in A1 and i in A2 and i in A3]
out['four_coder_n'] = len(ids)
out['four_coder_include_fleiss'] = fleiss([[H[i]['include']] + [A[i]['include'].strip().lower() for A in (A1, A2, A3)] for i in ids])
out['human_n_included'] = sum(H[i]['include'] == 'yes' for i in H)
json.dump(out, open(os.path.join(ROOT, 'results', 'human_agreement.json'), 'w'), indent=1)
print(json.dumps(out, indent=1))
