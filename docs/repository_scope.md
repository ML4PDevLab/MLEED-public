# Repository scope and publication release

The publication target is a data descriptor documenting construction, records, validation, limitations, and reuse. This package supports those functions with a fixed national panel and independently checkable numeric summaries.

## Available now

| Material | Status |
| --- | --- |
| National country-month data | 69 countries, January 2012–December 2025; original bytes preserved |
| Dictionaries | Human-readable descriptions, all 88 machine-readable fields, exact country names |
| Coverage and category summaries | Rebuilt from the public CSV |
| Structural validation | Schema, dates, keys, finite integer counts, label totals, normalization, binary domains |
| Indicator diagnostics | 36 differences from a literal count-screen comparison |
| Classifier validation | Six numeric aggregate files checked against 431-case confusion matrices |
| Human-review summary | Purposive surge audit, with incomplete error accounting disclosed |
| Reuse code | Category pooling and reporting rates, with tested safeguards |
| File identity | Explicit manifest, SHA-256 checksums, snapshot metadata |

## Materials outside this package

Full news text, individual predictions, credentials, database dumps, third-party benchmark datasets, and manuscript drafts are excluded. National data do not confer rights over source publishers' text. The national and subnational dashboards remain companion products with potentially different inclusion rules and refresh schedules. No subnational data or 71-country extension is part of this national file.

The scripts validate and transform deposited aggregates. They do not reproduce collection, translation, training, inference, geographic extraction, or historical surge fitting. Current operational code is not evidence that its exact version produced an older CSV.

An audit on 29 September 2026 distinguished this fixed file from [a newer dashboard dataset](https://huggingface.co/datasets/zungru/mlp-counts/tree/b03f4a9bccea12f9608e4efcafc33bec2600657c). That pinned snapshot contains complete fields for 70 countries through April 2026, while May has zero-document and missing-normalized-value gaps. Complete aggregate fields do not certify collection or processing completeness. The audit does not support a 71-country release complete through mid-2026, so this repository retains the verified 69-country file and its actual endpoint.

## Requirements before a completed submission deposit

1. Confirm the snapshot and country-month collection completeness. If extending to 71 countries or 2026, export and audit new aggregates, document the cutoff and changes, and preserve this snapshot.
2. Record authorized code and data licenses; both remain unspecified.
3. Link the national export to frozen extraction code, model versions, inference settings, source inclusion rules, and geographic versions. Supply reproducible code without credentials or unintended database writes.
4. Reconcile the historical surge algorithms, 36 indicator discrepancies, and human-audit error accounting. Distinguish top-one and top-two scoring.
5. Document evaluation split construction and linkage to model weights. Supply annotation guidance and safe test identifiers or an access route where rights permit.
6. Archive the approved release in a suitable persistent repository, obtain a DOI, create a versioned GitHub release, and cite that version in the manuscript. A dashboard and a mutable GitHub branch do not substitute for an archived dataset.
7. Check manuscript availability claims against the archive inventory. Do not describe unresolved licenses, missing code, or an uncreated DOI as completed.

Metadata use `null` for unassigned licenses and DOI and `false` for unverified completeness and historical version linkage. These are explicit open items, not fields to fill by inference.
