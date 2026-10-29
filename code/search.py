"""Systematic Europe PMC search: AI/ML x organoids / organs-on-chips, 2015-2026.

Writes search/records.jsonl (all hits with abstracts), search/search_log.json (query, date, counts).
Run: python code/search.py
"""
import datetime, json, os, time, urllib.parse, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'search')
NAM = ('(TITLE_ABS:organoid* OR TITLE_ABS:"organ-on-a-chip" OR TITLE_ABS:"organ-on-chip" OR TITLE_ABS:"organs-on-chips" '
       'OR TITLE_ABS:"organs-on-a-chip" OR TITLE_ABS:"microphysiological system*" OR TITLE_ABS:"tissue chip*")')
AI = ('(TITLE_ABS:"machine learning" OR TITLE_ABS:"deep learning" OR TITLE_ABS:"artificial intelligence" '
      'OR TITLE_ABS:"neural network*" OR TITLE_ABS:"convolutional" OR TITLE_ABS:"random forest" '
      'OR TITLE_ABS:"transformer*" OR TITLE_ABS:"computer vision")')
QUERY = f'{NAM} AND {AI} AND PUB_YEAR:[2015 TO 2026]'


def fetch():
    recs, cursor = [], '*'
    while True:
        url = ('https://www.ebi.ac.uk/europepmc/webservices/rest/search?format=json&resultType=core&pageSize=500'
               f'&cursorMark={urllib.parse.quote(cursor)}&query={urllib.parse.quote(QUERY)}')
        for _ in range(5):
            try:
                r = json.load(urllib.request.urlopen(url, timeout=120)); break
            except Exception as e:
                print('retry', e); time.sleep(5)
        res = r['resultList']['result']
        for x in res:
            recs.append(dict(
                id=x.get('id'), source=x.get('source'), doi=x.get('doi'), pmid=x.get('pmid'), pmcid=x.get('pmcid'),
                title=x.get('title', ''), abstract=x.get('abstractText', ''), year=int(x.get('pubYear', 0) or 0),
                journal=(x.get('journalInfo') or {}).get('journal', {}).get('medlineAbbreviation') or (x.get('bookOrReportDetails') or {}).get('publisher', ''),
                first_author=(x.get('authorList') or {}).get('author', [{}])[0].get('lastName', x.get('authorString', '').split(',')[0]),
                authors=x.get('authorString', ''),
                pub_types=(x.get('pubTypeList') or {}).get('pubType', []),
                cited_by=x.get('citedByCount', 0), is_preprint=x.get('source') == 'PPR',
                oa=x.get('isOpenAccess') == 'Y'))
        nxt = r.get('nextCursorMark')
        print(len(recs), '/', r['hitCount'])
        if not res or nxt == cursor:
            break
        cursor = nxt
    return recs, r['hitCount']


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    recs, n = fetch()
    with open(os.path.join(OUT, 'records.jsonl'), 'w', encoding='utf-8') as fh:
        for x in recs:
            fh.write(json.dumps(x, ensure_ascii=False) + '\n')
    json.dump(dict(query=QUERY, database='Europe PMC REST API', date=datetime.date.today().isoformat(), hits=n,
                   retrieved=len(recs)), open(os.path.join(OUT, 'search_log.json'), 'w'), indent=1)
