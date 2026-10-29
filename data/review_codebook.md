# Review relevance codebook

For each record (indexed as a review), decide from title + abstract:

- `core` — the review is mainly about AI / machine learning applied to organoids and/or organs-on-chips / microphysiological systems (e.g. "AI-enabled organoids", "organ-on-chip meets AI").
- `partial` — the review is mainly about organoids, organs-on-chips, NAMs or 3D models, and AI/ML is one of several topics covered (a section or a stated theme), OR mainly about AI in drug discovery/biology with organoids/chips as one of several topics.
- `off_topic` — AI and organoids/chips are only mentioned in passing; the review is about something else (e.g. natural products, a disease, iPSC biology, cardiac development).
- `not_a_review` — the record is actually a primary study, editorial or protocol despite the review index.

Output CSV header: `id,relevance,reason` (reason ≤12 words).
