"""Build browser/index.html: a single-file searchable view of data/database.csv."""
import csv, json, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
rows = list(csv.DictReader(open(os.path.join(ROOT, 'data', 'database.csv'), encoding='utf-8')))
keep = ['year', 'first_author', 'title', 'journal', 'doi', 'preprint', 'system', 'tissue', 'ai_task', 'application',
        'validation', 'human_relevance_benchmark', 'regulatory_mention']
data = [{k: r[k] for k in keep} for r in rows]
html = open(os.path.join(ROOT, 'browser', 'template.html'), encoding='utf-8').read()
html = html.replace('/*__DATA__*/', 'const DATA = ' + json.dumps(data, ensure_ascii=False) + ';')
open(os.path.join(ROOT, 'browser', 'index.html'), 'w', encoding='utf-8').write(html)
print(len(data), 'studies')
