"""Merge extraction batches, compute the systematic-map statistics and inter-coder agreement.

Writes data/database.csv (included studies with bibliographic fields), results/summary.json,
results/crosstabs.json.  Run: python code/analyse.py
"""
import collections, csv, glob, json, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, 'data'); RES = os.path.join(ROOT, 'results'); os.makedirs(RES, exist_ok=True)
FIELDS = ['system', 'tissue', 'tumour', 'patient_derived', 'data_type', 'ai_task', 'ai_family', 'application',
          'validation', 'human_relevance_benchmark', 'open_code_or_data', 'regulatory_mention']
VAL_ORDER = ['none_reported', 'internal_split_or_cv', 'external_dataset', 'experimental_prospective', 'clinical_outcome']

recs = {}
for l in open(os.path.join(ROOT, 'search', 'records.jsonl'), encoding='utf-8'):
    x = json.loads(l); recs[x['id']] = x
rows = []
for f in sorted(glob.glob(os.path.join(D, 'extract_batch*.csv'))):
    rows += list(csv.DictReader(open(f, encoding='utf-8')))
S = {}
S['screened'] = len(rows)
dup = {r['drop_id'] for r in csv.DictReader(open(os.path.join(D, 'duplicates.csv'), encoding='utf-8'))}
inc_all = [r for r in rows if r['include'].strip().lower() == 'yes']
inc = [r for r in inc_all if r['id'] not in dup]
S['included_before_dedupe'] = len(inc_all); S['duplicates_removed'] = len(inc_all) - len(inc)
exc = [r for r in rows if r['include'].strip().lower() != 'yes']
S['included'] = len(inc)
S['excluded'] = len(exc)
S['exclude_reasons'] = dict(collections.Counter(r['exclude_reason'] for r in exc).most_common())
dedupe = json.load(open(os.path.join(ROOT, 'search', 'dedupe_log.json')))
log = json.load(open(os.path.join(ROOT, 'search', 'search_log.json')))
S['search_hits'] = log['hits']; S['search_date'] = log['date']; S.update({'dedupe_' + k: v for k, v in dedupe.items()})


def split(v):
    return [t.strip() for t in (v or '').split(';') if t.strip()]


def counts(field, multi=True):
    c = collections.Counter()
    for r in inc:
        for t in (split(r[field]) if multi else [r[field].strip()]):
            c[t] += 1
    return dict(c.most_common())


for f in FIELDS:
    S['n_' + f] = counts(f)
pct = lambda k, n=None: round(100 * k / (n or len(inc)), 1)
# headline numbers
years = collections.Counter(recs[r['id']]['year'] for r in inc)
S['included_by_year'] = dict(sorted(years.items()))
S['included_2025_2026'] = years.get(2025, 0) + years.get(2026, 0)
S['pct_included_2025_2026'] = pct(S['included_2025_2026'])
S['included_preprints'] = sum(recs[r['id']]['is_preprint'] for r in inc)


def highest_val(r):
    v = split(r['validation'])
    return max(v, key=VAL_ORDER.index) if v and all(x in VAL_ORDER for x in v) else 'none_reported'


hv = collections.Counter(highest_val(r) for r in inc)
S['validation_highest'] = {k: hv.get(k, 0) for k in VAL_ORDER}
S['pct_validation'] = {k: pct(hv.get(k, 0)) for k in VAL_ORDER}
beyond = sum(hv[k] for k in VAL_ORDER[2:])
S['n_beyond_internal'] = beyond; S['pct_beyond_internal'] = pct(beyond)
S['n_clinical_outcome'] = hv.get('clinical_outcome', 0)
hb = collections.Counter(r['human_relevance_benchmark'].strip() for r in inc)
S['n_any_in_vivo_benchmark'] = hb['animal'] + hb['clinical'] + hb['both']; S['pct_any_in_vivo_benchmark'] = pct(S['n_any_in_vivo_benchmark'])
S['n_animal_benchmark'] = hb['animal'] + hb['both']
S['n_open'] = sum(r['open_code_or_data'].strip() == 'yes' for r in inc); S['pct_open'] = pct(S['n_open'])
S['n_regulatory'] = sum(r['regulatory_mention'].strip() == 'yes' for r in inc); S['pct_regulatory'] = pct(S['n_regulatory'])
tox = [r for r in inc if 'toxicity_safety' in split(r['application'])]
S['n_toxicity'] = len(tox); S['pct_toxicity'] = pct(len(tox))
S['tox_beyond_internal'] = sum(highest_val(r) in VAL_ORDER[2:] for r in tox)
S['tox_in_vivo_benchmark'] = sum(r['human_relevance_benchmark'].strip() in ('animal', 'clinical', 'both') for r in tox)
img = [r for r in inc if any(t.endswith('image') for t in split(r['data_type']))]
S['n_image'] = len(img); S['pct_image'] = pct(len(img))
S['n_tumour'] = sum(r['tumour'].strip() == 'yes' for r in inc); S['pct_tumour'] = pct(S['n_tumour'])
S['n_patient_derived'] = sum(r['patient_derived'].strip() == 'yes' for r in inc); S['pct_patient_derived'] = pct(S['n_patient_derived'])
chips = [r for r in inc if r['system'].strip() in ('organ_on_chip', 'organoid_on_chip', 'multiple')]
S['n_chip_any'] = len(chips); S['pct_chip_any'] = pct(len(chips))
S['n_organoid_only'] = sum(r['system'].strip() == 'organoid' for r in inc)
S['n_llm_or_generative'] = sum('generative_or_llm' in split(r['ai_task']) or 'llm' in split(r['ai_family']) for r in inc)
S['n_transformer'] = sum('transformer_or_foundation' in split(r['ai_family']) for r in inc)
S['n_reviews_in_search'] = dedupe['excluded_review_pubtype']
S['pct_reviews_in_search'] = round(100 * dedupe['excluded_review_pubtype'] / log['hits'], 1)

# crosstab: application x highest validation
ct = collections.defaultdict(collections.Counter)
for r in inc:
    for a in split(r['application']):
        ct[a][highest_val(r)] += 1
json.dump({a: {k: c.get(k, 0) for k in VAL_ORDER} for a, c in ct.items()}, open(os.path.join(RES, 'crosstab_application_validation.json'), 'w'), indent=1)
# reviews by year (from search) vs included primary by year
rev_years = collections.Counter(x['year'] for x in recs.values() if any('review' in t.lower() for t in x['pub_types']))
S['reviews_by_year'] = dict(sorted(rev_years.items()))

# inter-coder agreement on the QC sample
qc_path = os.path.join(D, 'extract_qc_second_coder.csv')
if os.path.exists(qc_path):
    second = {r['id']: r for r in csv.DictReader(open(qc_path, encoding='utf-8'))}
    first = {r['id']: r for r in rows}
    ids = [i for i in second if i in first]

    def kappa(a, b):
        n = len(a); po = sum(x == y for x, y in zip(a, b)) / n
        ca, cb = collections.Counter(a), collections.Counter(b)
        pe = sum(ca[k] * cb[k] for k in set(ca) | set(cb)) / n ** 2
        return po, (po - pe) / (1 - pe) if pe < 1 else 1.0
    inc_a = [first[i]['include'].strip().lower() for i in ids]; inc_b = [second[i]['include'].strip().lower() for i in ids]
    po, k = kappa(inc_a, inc_b)
    S['qc_n'] = len(ids); S['qc_include_agreement_pct'] = round(100 * po, 1); S['qc_include_kappa'] = round(k, 2)
    both = [i for i in ids if first[i]['include'].strip().lower() == 'yes' == second[i]['include'].strip().lower()]
    S['qc_both_included'] = len(both)
    for f in ['system', 'application', 'validation', 'ai_task']:
        a = [first[i][f].strip() for i in both]; b = [second[i][f].strip() for i in both]
        if both:
            po, k = kappa(a, b)
            S[f'qc_{f}_agreement_pct'] = round(100 * po, 1); S[f'qc_{f}_kappa'] = round(k, 2)

# database
with open(os.path.join(D, 'database.csv'), 'w', newline='', encoding='utf-8') as fh:
    w = csv.writer(fh)
    w.writerow(['year', 'first_author', 'title', 'journal', 'doi', 'pmid', 'preprint'] + FIELDS + ['n_samples', 'notes'])
    for r in sorted(inc, key=lambda r: (-recs[r['id']]['year'], recs[r['id']]['first_author'] or '')):
        x = recs[r['id']]
        w.writerow([x['year'], x['first_author'], x['title'], x['journal'], x['doi'] or '', x['pmid'] or '',
                    'yes' if x['is_preprint'] else 'no'] + [r[f] for f in FIELDS] + [r['n_samples'], r['notes']])
json.dump(S, open(os.path.join(RES, 'summary.json'), 'w'), indent=1)
print(json.dumps(S, indent=1))
