"""Relevance of the 541 records indexed as reviews, from a random sample of 60 coded by two coders.

Writes results/review_relevance.json.
"""
import collections, csv, json, math, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
A = {r['id']: r['relevance'] for r in csv.DictReader(open(os.path.join(ROOT, 'data', 'review_relevance_A.csv'), encoding='utf-8'))}
B = {r['id']: r['relevance'] for r in csv.DictReader(open(os.path.join(ROOT, 'data', 'review_relevance_B.csv'), encoding='utf-8'))}
S = json.load(open(os.path.join(ROOT, 'results', 'summary.json')))
ids = sorted(A)
n = len(ids); N = S['n_reviews_in_search']


def kappa(a, b):
    po = sum(x == y for x, y in zip(a, b)) / len(a)
    ca, cb = collections.Counter(a), collections.Counter(b)
    pe = sum(ca[k] * cb[k] for k in set(ca) | set(cb)) / len(a) ** 2
    return po, (po - pe) / (1 - pe)


def wilson(k, n, z=1.96):
    p = k / n; d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d; h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return c - h, c + h


po, k = kappa([A[i] for i in ids], [B[i] for i in ids])
on = lambda c: c in ('core', 'partial')
po2, k2 = kappa([on(A[i]) for i in ids], [on(B[i]) for i in ids])
# consensus: on-topic only if both coders say so (conservative); core only if both say core
cons_on = sum(on(A[i]) and on(B[i]) for i in ids)
any_on = sum(on(A[i]) or on(B[i]) for i in ids)
cons_core = sum(A[i] == 'core' and B[i] == 'core' for i in ids)
lo, hi = wilson(cons_on, n); lo2, hi2 = wilson(any_on, n); clo, chi = wilson(cons_core, n)
out = dict(sample_n=n, reviews_total=N,
           counts_A=dict(collections.Counter(A.values())), counts_B=dict(collections.Counter(B.values())),
           agreement_4class_pct=round(100 * po, 1), kappa_4class=round(k, 2),
           agreement_ontopic_pct=round(100 * po2, 1), kappa_ontopic=round(k2, 2),
           ontopic_both=cons_on, ontopic_either=any_on, core_both=cons_core,
           pct_ontopic_both=round(100 * cons_on / n, 1), pct_ontopic_either=round(100 * any_on / n, 1),
           est_ontopic_reviews_low=round(N * cons_on / n), est_ontopic_reviews_high=round(N * any_on / n),
           est_ontopic_ci=[round(N * lo), round(N * hi2)],
           pct_core_both=round(100 * cons_core / n, 1), est_core_reviews=round(N * cons_core / n),
           est_core_ci=[round(N * clo), round(N * chi)],
           pct_offtopic_A=round(100 * collections.Counter(A.values())['off_topic'] / n, 1),
           pct_offtopic_B=round(100 * collections.Counter(B.values())['off_topic'] / n, 1))
out['ratio_ontopic_reviews_per_study_low'] = round(out['est_ontopic_reviews_low'] / S['included'], 2)
out['ratio_ontopic_reviews_per_study_high'] = round(out['est_ontopic_reviews_high'] / S['included'], 2)
json.dump(out, open(os.path.join(ROOT, 'results', 'review_relevance.json'), 'w'), indent=1)
print(json.dumps(out, indent=1))
