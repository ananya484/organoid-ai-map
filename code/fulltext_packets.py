# -*- coding: utf-8 -*-
"""Build blinded full-text packets for validation coding: for each open-access included study, the abstract plus
every Methods/Results paragraph that mentions training, testing, validation, cohorts or comparison with in vivo data
(capped at 9,000 characters). Abstract-level codes are not included. Writes data/fulltext_packets/batch{1-6}.md."""
import csv
import random
import re
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'data' / 'fulltext_packets'; OUT.mkdir(exist_ok=True)
KEY = re.compile(r'valid|test(ed|ing)? set|held[- ]out|hold[- ]out|independent|external|cross[- ]valid|fold|train|'
                 r'cohort|patient|clinical|in vivo|mouse|mice|rat|xenograft|animal|prospective|blind|unseen|'
                 r'generali[sz]|benchmark|accuracy|AUC|ROC|sensitivity|specificity|F1|precision|recall', re.I)
CAP = 9000


def text(el):
    return ' '.join(''.join(el.itertext()).split())


ids = [r['pmcid'] for r in csv.DictReader(open(ROOT / 'results' / 'fulltext_code_check.csv', encoding='utf-8'))]
packets = []
for pmcid in ids:
    root = ET.parse(ROOT / 'search' / 'fulltext' / f'{pmcid}.xml').getroot()
    title = text(root.find('.//article-title')) if root.find('.//article-title') is not None else ''
    abst = ' '.join(text(a) for a in root.iter('abstract'))
    paras = []
    for sec in root.iter('sec'):
        st = sec.find('title')
        stitle = (text(st) if st is not None else '').lower()
        if re.search(r'introduction|background|discussion|conclusion|acknowledg|funding|author|competing|reference', stitle):
            continue
        for p in sec.findall('p'):
            t = text(p)
            if KEY.search(t) and t not in paras:
                paras.append(t)
    body, n = [], 0
    for t in paras:
        if n + len(t) > CAP:
            break
        body.append(t); n += len(t)
    packets.append(f'## {pmcid}\n**Title:** {title}\n\n**Abstract:** {abst}\n\n**Methods/Results excerpts:**\n\n' + '\n\n'.join(body) + '\n')
random.seed(7)
order = list(range(len(packets))); random.shuffle(order)
for b in range(6):
    sel = [packets[i] for i in order[b::6]]
    (OUT / f'batch{b + 1}.md').write_text('\n---\n\n'.join(sel), encoding='utf-8')
    print(b + 1, len(sel), sum(len(s) for s in sel))
