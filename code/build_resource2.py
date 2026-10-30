# -*- coding: utf-8 -*-
"""Build submission/OnlineResource2_database_code.zip. Abstracts and full-text extracts belong to the publishers and
are left out: abstracts are stripped from search/*.jsonl, and the full-text packets are rebuilt from PubMed Central by
code/fulltext_packets.py."""
import io
import json
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKIP_DIRS = {'search/fulltext', 'search/s2_batches'}
pats = ['code/*.py', 'data/*.csv', 'data/*.md', 'data/*.xlsx', 'data/fulltext_packets/INSTRUCTIONS.md',
        'data/fulltext_packets/coded_*.csv', 'results/*', 'search/*.json', 'search/*.jsonl', 'browser/*', 'README.md']
files = sorted({p for pat in pats for p in ROOT.glob(pat) if p.is_file()})
files = [p for p in files if p.name not in ('search_openalex.py', 'openalex_log.json', 'human_coding_60.xlsx')]  # sheet holds abstracts
out = ROOT / 'submission' / 'OnlineResource2_database_code.zip'
with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED) as z:
    for p in files:
        rel = p.relative_to(ROOT).as_posix()
        if p.suffix == '.jsonl':
            buf = io.StringIO()
            for line in p.read_text(encoding='utf-8').splitlines():
                if line.strip():
                    rec = json.loads(line); rec.pop('abstract', None)
                    buf.write(json.dumps(rec, ensure_ascii=False) + '\n')
            z.writestr(rel, buf.getvalue())
        else:
            z.write(p, rel)
print(len(files), 'files ->', out)
