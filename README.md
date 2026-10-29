# OrganoidAI Map

A searchable, coded database of every primary study (2018–2026) that applied machine learning to **organoids** or **organs-on-chips**, built for a systematic map of the evidence relevant to regulatory use as a new approach methodology (NAM).

**Browse the database:** https://ananya-sharma-bio.github.io/organoid-ai-map/ *(update this link after enabling GitHub Pages)*

> Sharma A (2026) A review for almost every study: a systematic map of artificial intelligence applied to organoids and organs-on-chips, and the evidence a regulator would need. Preprint. *(DOI to be added)*

## What is here
| Path | Contents |
|---|---|
| `browser/index.html` | Searchable database (filters for system, application, validation, in vivo comparison). Works offline. |
| `data/database.csv` | The 245 included studies with bibliographic details and codes |
| `data/codebook.md` | Screening and extraction codebook |
| `data/extract_batch*.csv` | Every screening and extraction decision (566 records) |
| `data/extract_qc_*` | Second and third independent coders on a 60-record sample |
| `data/recheck_log.csv`, `data/duplicates.csv` | Re-checked key records; merged preprint/journal pairs |
| `data/review_relevance_*.csv` | Relevance coding of a sample of 60 records indexed as reviews |
| `search/` | Query, search log, retrieved record metadata (abstracts removed for copyright; `code/search.py` re-fetches them) |
| `results/` | Summary statistics, agreement, full-text openness check |
| `code/` | All scripts |

## Headline numbers
245 studies · 222 organoid, 23 organ-on-chip · 64.5% report no validation · 17.1% validated beyond an internal split · 14 compared predictions with in vivo outcomes · 2 with animal or preclinical data · 18 address toxicity/safety.

## Reproduce
```
pip install numpy scipy matplotlib
python code/search.py            # re-runs the Europe PMC search (records grow over time)
python code/analyse.py
python code/fulltext_code_check.py
python code/make_figures.py
python code/build_browser.py
```

## Contribute
Missed a study, or a code looks wrong? Open an issue with the DOI and the field to change. The database will be updated.

## Licence
Data and text: CC BY 4.0. Code: MIT. See `LICENSE`.
