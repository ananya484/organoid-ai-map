# Screening and extraction codebook (title + abstract)

One row per record. Code ONLY from the title and abstract given. Never guess; use `unclear` when the abstract does not say.

## Inclusion
include = `yes` only if ALL hold:
1. Primary study (new data, new model, new method or new analysis). Not a review, perspective, editorial, protocol-only, commentary, conference abstract without results.
2. Uses a human or animal **organoid**, **spheroid-in-organoid sense**, **organ-on-chip / microphysiological system / tissue chip**, or organoid-on-chip as the experimental system.
3. Applies an AI / machine-learning method (ML, deep learning, neural network, random forest, SVM, gradient boosting, transformer, LLM, computer vision with learned models) to data FROM that system, or uses AI to design/control that system.

Otherwise include = `no` and give `exclude_reason` from:
`not_primary` | `no_organoid_or_chip` (system is 2D culture, animals, patients only, simple spheroid aggregates not called organoids) | `no_ai` (only statistics, mechanistic modelling, "intelligent" wording) | `organoid_intelligence_computing` (brain organoids used as a computing substrate / biocomputing) | `other` (explain in notes).

Organoid intelligence / biocomputing papers: include=`no`, reason `organoid_intelligence_computing` (counted separately).

## Fields for included records (use exactly these codes; `;` to separate multiple)
- `system`: organoid | organ_on_chip | organoid_on_chip | multiple
- `tissue`: brain | retina | intestine_colon | stomach | liver | pancreas | kidney | lung | heart | vascular | skin | breast | tumour_other | bone_cartilage | reproductive | multi | other
- `tumour`: yes | no  (tumour/cancer organoids or tumour-on-chip)
- `patient_derived`: yes | no | unclear
- `data_type`: brightfield_image | fluorescence_image | other_image (OCT, EM, etc.) | transcriptomics | other_omics | electrophysiology | sensor_timeseries | drug_response_values | multimodal | other
- `ai_task`: segmentation_detection | morphology_classification | drug_response_prediction | toxicity_prediction | omics_analysis | signal_analysis | system_design_optimisation | generative_or_llm | tracking_timelapse | other
- `ai_family`: classical_ml | cnn | transformer_or_foundation | other_deep | llm | unclear
- `application`: disease_modelling | drug_efficacy_screening | toxicity_safety | personalised_medicine | quality_control | device_or_protocol_design | method_development
- `validation`: none_reported | internal_split_or_cv | external_dataset | experimental_prospective | clinical_outcome
  (highest level reported. `external_dataset` = data from another lab/cohort/batch explicitly held out. `experimental_prospective` = new wet-lab experiment designed to test the model's predictions. `clinical_outcome` = predictions compared with patient response or clinical data.)
- `human_relevance_benchmark`: animal | clinical | both | none  (were organoid/chip-based predictions compared with animal or human in vivo outcomes?)
- `n_samples`: number as stated (organoids, images, patients or chips; give unit, e.g. "1200 images", "45 patients"), else `unclear`
- `open_code_or_data`: yes | unclear  (yes only if abstract says code/data/tool is publicly available)
- `regulatory_mention`: yes | no  (abstract mentions NAMs, animal replacement/3Rs, FDA, regulatory acceptance)
- `notes`: ≤15 words, optional

## Output
CSV with header:
`id,include,exclude_reason,system,tissue,tumour,patient_derived,data_type,ai_task,ai_family,application,validation,human_relevance_benchmark,n_samples,open_code_or_data,regulatory_mention,notes`
For excluded rows, leave fields after exclude_reason empty except notes. Quote any field containing commas.
