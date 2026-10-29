"""Full-text check of code/data sharing for included open-access studies.

For every included study with a PMCID, fetch the Europe PMC full-text XML and look for links
to code or data repositories. Writes results/fulltext_code_check.csv and adds counts to
results/fulltext_summary.json.  Run after analyse.py.
"""
import csv, json, os, re, time, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES = os.path.join(ROOT, 'results'); CACHE = os.path.join(ROOT, 'search', 'fulltext'); os.makedirs(CACHE, exist_ok=True)
recs = {}
for l in open(os.path.join(ROOT, 'search', 'records.jsonl'), encoding='utf-8'):
    x = json.loads(l); recs[x['id']] = x
db = list(csv.DictReader(open(os.path.join(ROOT, 'data', 'database.csv'), encoding='utf-8')))
by_title = {x['title']: x for x in recs.values()}
CODE = re.compile(r'github\.com|gitlab\.com|bitbucket\.org|code ocean|codeocean\.com|zenodo\.org|figshare\.com|huggingface\.co', re.I)
DATA = re.compile(r'\bGSE\d{4,}|\bPRJNA\d+|ebi\.ac\.uk/(?:biostudies|pride|arrayexpress)|idr\.openmicroscopy|dryad|osf\.io|synapse\.org|zenodo\.org|figshare\.com', re.I)
EXT = re.compile(r'external(?:ly)?[ -](?:validat|test|cohort|dataset)|independent (?:test|validation|cohort|dataset)|held[- ]out (?:test|dataset|cohort)', re.I)
VIVO = re.compile(r'xenograft|patient response|clinical response|treatment response of (?:the )?patients|in vivo efficacy|animal (?:model|stud)', re.I)
rows = []
for d in db:
    x = by_title.get(d['title'])
    if not x or not x.get('pmcid'):
        continue
    path = os.path.join(CACHE, x['pmcid'] + '.xml')
    if not os.path.exists(path):
        url = f"https://www.ebi.ac.uk/europepmc/webservices/rest/{x['pmcid']}/fullTextXML"
        try:
            txt = urllib.request.urlopen(url, timeout=60).read().decode('utf-8', 'ignore')
        except Exception:
            txt = ''
        open(path, 'w', encoding='utf-8').write(txt)
        time.sleep(0.2)
    txt = open(path, encoding='utf-8').read()
    if len(txt) < 2000:
        continue
    rows.append([x['pmcid'], d['year'], d['first_author'], bool(CODE.search(txt)), bool(DATA.search(txt)), d['open_code_or_data'], bool(EXT.search(txt)), bool(VIVO.search(txt)), d['validation']])
with open(os.path.join(RES, 'fulltext_code_check.csv'), 'w', newline='', encoding='utf-8') as fh:
    w = csv.writer(fh); w.writerow(['pmcid', 'year', 'first_author', 'code_repo_link', 'data_repo_link', 'abstract_says_open', 'fulltext_external_validation_terms', 'fulltext_in_vivo_terms', 'abstract_validation']); w.writerows(rows)
n = len(rows)
S = dict(fulltext_n=n, fulltext_code_link=sum(r[3] for r in rows), fulltext_data_link=sum(r[4] for r in rows),
         fulltext_any_link=sum(r[3] or r[4] for r in rows))
S['fulltext_pct_code_link'] = round(100 * S['fulltext_code_link'] / n, 1)
S['fulltext_pct_any_link'] = round(100 * S['fulltext_any_link'] / n, 1)
S['fulltext_ext_terms'] = sum(r[6] for r in rows); S['fulltext_pct_ext_terms'] = round(100 * S['fulltext_ext_terms'] / n, 1)
S['fulltext_vivo_terms'] = sum(r[7] for r in rows); S['fulltext_pct_vivo_terms'] = round(100 * S['fulltext_vivo_terms'] / n, 1)
S['fulltext_pct_no_link'] = round(100 - S['fulltext_pct_any_link'], 1)
json.dump(S, open(os.path.join(RES, 'fulltext_summary.json'), 'w'), indent=1)
print(S)
