# Full-text validation coding

For each study (## PMCxxxx) read the abstract and the Methods/Results excerpts and code, from the FULL TEXT given:

- `validation_ft`: highest level of validation of the machine-learning model actually performed and reported:
  - `none_reported`: no quantitative evaluation of the model on held-out data.
  - `internal_split_or_cv`: train/test split, cross-validation or held-out images/organoids from the same dataset, lab and batch. Evaluation of a segmentation tool against manual annotation of held-out images counts here.
  - `external_dataset`: tested on data the model never saw that come from another lab, cohort, donor set, batch or imaging system that is explicitly described as independent/external.
  - `experimental_prospective`: a new wet-lab experiment designed to test the model's predictions (e.g. predicted hits re-tested).
  - `clinical_outcome`: model predictions compared with patient response, survival or clinical data.
  Code the highest level that is genuinely performed for the ML model, not one mentioned only as future work or background.
- `human_relevance_benchmark_ft`: `animal` | `clinical` | `both` | `none` — were organoid/chip-based model predictions compared with animal or human in vivo outcomes?
- `unit_independence`: `donor_or_patient` | `batch_or_lab` | `compound` | `image_or_organoid_only` | `unclear` — the unit by which training and test data were separated (best evidence in the text).
- `ft_notes`: ≤15 words of evidence (e.g. "held-out cohort of 40 patients from second hospital").

Judge each paper individually; do not guess from keywords. If the excerpts are insufficient, code conservatively and say so in ft_notes.

Output: write a CSV with header
`pmcid,validation_ft,human_relevance_benchmark_ft,unit_independence,ft_notes`
one row per study, all studies in your file, quote fields containing commas.
