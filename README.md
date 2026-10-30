# OrganoidAI Map

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.23778313.svg)](https://doi.org/10.5281/zenodo.23778313)

A searchable, coded database of every primary study (2018–2026) that applied machine learning to **organoids** or **organs-on-chips**, built for a systematic map of the evidence relevant to regulatory use as a new approach methodology (NAM).

**Browse the database:** https://ananya484.github.io/organoid-ai-map/

> Sharma A (2026) OrganoidAI Map: a systematic map and coded database of machine-learning studies on organoids and organs-on-chips. Preprint. *(DOI to be added)*

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
| `data/fulltext_validation.csv`, `data/fulltext_packets/` | Full-text validation coding of the 127 open-access studies (instructions, both coders; extracts rebuilt from PMC by `code/fulltext_packets.py`) |
| `data/s2_included.csv`, `data/extract_s2_batch*.csv` | Supplementary Semantic Scholar search: 350 screened, 105 further studies (mostly meeting abstracts and conference papers), coded separately |
| `search/` | Query, search log, retrieved record metadata (abstracts removed for copyright; `code/search.py` re-fetches them) |
| `results/` | Summary statistics, agreement, full-text openness check |
| `code/` | All scripts |

## Headline numbers
245 studies · 222 organoid, 23 organ-on-chip · 64.5% report no validation in the abstract (22.0% in open-access full texts) · 17.1% validated beyond an internal split (20.5% in full texts) · 15.7% keep train/test independent by donor, batch or compound · 14 compared predictions with in vivo outcomes · 2 with animal or preclinical data · 18 address toxicity/safety.

## Reproduce
```
pip install numpy scipy matplotlib
python code/search.py            # re-runs the Europe PMC search (records grow over time)
python code/analyse.py
python code/fulltext_code_check.py
python code/fulltext_packets.py     # then code the packets (data/fulltext_packets/INSTRUCTIONS.md)
python code/fulltext_validation.py
python code/search_s2.py; python code/dedupe_s2.py; python code/s2_supplement.py
python code/make_figures.py
python code/build_browser.py
```

## Changelog
- **v1.1.0 (31 Oct 2026):** full-text validation coding of the open-access studies; supplementary Semantic Scholar search; Fleiss reference added.
- **v1.0.0 (30 Oct 2026):** first release.

## Contribute
Missed a study, or a code looks wrong? Open an issue with the DOI and the field to change. The database will be updated.

## Cite the database
Sharma A (2026) OrganoidAI Map: a coded database of machine-learning studies on organoids and organs-on-chips (v1.0.0). Zenodo. https://doi.org/10.5281/zenodo.23778313

## Licence
Data and text: CC BY 4.0. Code: MIT. See `LICENSE`.
