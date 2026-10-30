# -*- coding: utf-8 -*-
"""Fetch Crossref metadata for every candidate DOI and store it in refs_verified.json."""
import json
import time
import urllib.parse
import urllib.request
from pathlib import Path

DOIS = [
    "10.1038/nature07935", "10.1038/nature12517", "10.1038/s41568-018-0007-6", "10.1126/science.aao2774",
    "10.1126/science.1188302", "10.1038/nbt.2989", "10.1038/s43586-022-00118-6", "10.1038/s41576-022-00466-9",
    "10.1038/s43856-022-00209-1", "10.14573/altex.2001241", "10.1186/s41231-019-0050-7", "10.1016/j.jacbts.2019.10.008",
    "10.1016/j.bioactmat.2023.09.005", "10.7150/thno.87266", "10.1016/j.envint.2023.108082",
    "10.1136/bmj-2023-078378", "10.7326/M18-0850", "10.1148/ryai.2020200029", "10.1038/s41592-021-01205-4",
    "10.1016/j.patter.2023.100804", "10.1177/001316446002000104", "10.3389/fsci.2023.1017235",
    "10.1038/s41467-020-19313-8", "10.1038/s41698-023-00480-y", "10.1016/j.xcrm.2025.102421", "10.1038/s41698-025-01082-6",
    "10.1038/s42003-025-08205-6", "10.1016/j.parkreldis.2020.05.011", "10.1088/1758-5090/ad38df",
    "10.1371/journal.pcbi.1010584", "10.1038/s41598-019-48874-y", "10.1242/dev.199611", "10.1371/journal.pone.0240802",
    "10.1016/j.celrep.2021.109429", "10.1038/s41467-023-38832-8", "10.1038/s41592-019-0686-2", "10.1038/s41586-020-2649-2",
    "10.1109/MCSE.2007.55", "10.11613/BM.2012.031",
    "10.64898/2026.04.10.26350512", "10.1126/sciadv.aef7756", "10.64898/2026.05.20.726675", "10.64898/2026.09.29.755355",
    "10.1016/j.stem.2026.07.004", "10.21203/rs.3.rs-8251435/v1", "10.1101/2025.07.08.663664", "10.3390/toxics12110809",
    "10.3390/cancers13153760", "10.1037/h0031619",
]

out = {}
for doi in DOIS:
    url = "https://api.crossref.org/works/" + urllib.parse.quote(doi)
    for attempt in range(4):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "refcheck/1.0 (mailto:ananya.sharma.pune@gmail.com)"})
            m = json.load(urllib.request.urlopen(req, timeout=60))["message"]
            break
        except Exception as e:
            err = str(e); time.sleep(2)
    else:
        print("FAIL", doi, err); continue
    authors = [f"{a.get('family','')} {''.join(x[0] for x in a.get('given','').replace('-', ' ').split())}".strip()
               for a in m.get("author", [])]
    out[doi] = dict(
        title=(m.get("title") or [""])[0],
        journal=(m.get("short-container-title") or m.get("container-title") or [""])[0],
        journal_full=(m.get("container-title") or [""])[0],
        year=(m.get("published-print") or m.get("published-online") or m.get("issued"))["date-parts"][0][0],
        volume=m.get("volume"), issue=m.get("issue"), pages=m.get("page"),
        article_number=m.get("article-number"), authors=authors)
    r = out[doi]
    print(doi, "|", r["year"], r["journal"], r["volume"], r["pages"] or r["article_number"], "|",
          (authors[0] if authors else "-"), "|", r["title"][:90].encode("ascii", "replace").decode())
    time.sleep(0.3)

(Path(__file__).resolve().parent.parent / "refs_verified.json").write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
print("n =", len(out))
