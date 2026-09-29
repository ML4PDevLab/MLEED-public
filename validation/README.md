# Aggregate validation evidence

This directory contains numeric summaries from the project evaluation archive. Source-file identities are recorded in [provenance.json](provenance.json); the package is covered by [SHA256SUMS](../SHA256SUMS). No news text or individual prediction records are included.

## Classifier reports

The separate [binary_confusion_matrix.csv](binary_confusion_matrix.csv) records the upstream environmental-relevance gate on 431 cases. Rows are true nonenvironmental/environmental labels; columns are predicted nonenvironmental/environmental labels. Counts are `[[164, 10], [0, 257]]`: 421 correct of 431 (97.680%). The positive-class precision is 257/267 and recall is 257/257.

This matrix was aggregated from the retained `binary_env` prediction field, where 0 means nonenvironmental and 1 means environmental. The reference negative is the exact `final_coding` value `-999`; all other reference categories, including environmental opinion and environmental -999, are positive. The private prediction artifact's basename, SHA-256, and extraction rules appear in [provenance.json](provenance.json). It contains publisher text and is not redistributed. The binary gate is distinct from the final multiclass output; collapsing the latter into environmental/nonenvironmental groups does not reproduce this matrix.

The six CSVs in `classification/` contain two raw confusion matrices, two row-normalized matrices, and two classification reports. Original filenames and bytes are preserved. Matrix rows are reference labels and columns are scored predicted labels. The first column holds label names. Counts total **431 cases**, including 174 `-999` nonenvironmental cases and 257 environmental cases including auxiliary classes. There are 20 labels: 17 substantive and three auxiliary.

| Scoring rule | Correct / cases | Accuracy | Weighted F1 |
| --- | --- | --- | --- |
| Primary prediction | 405 / 431 | 0.939675 | 0.941209 |
| Primary or secondary prediction | 408 / 431 | 0.946636 | 0.948180 |

The second rule credits either predicted category matching the reference. It is a permissive top-two evaluation, not standard single-prediction accuracy. Neither metric estimates accuracy for every country, language, year, or event type. Class support ranges from two to 174 cases, so pooled averages conceal differences in evidence by label.

Classification reports give precision, recall, F1, and support for each label, followed by macro and support-weighted averages. The original `accuracy` row repeats scalar accuracy across all four columns, including `support`; that entry is **not a sample count**. Obtain sample size from the confusion matrix or aggregate-average support.

Run `python scripts/verify_evaluation.py --check` to verify binary counts and metrics, multiclass scores, macro and weighted averages, accuracy, and row normalization against the deposited matrices. Results are saved in [evaluation_verification.json](../outputs/evaluation_verification.json).

A frozen link among training data, test split identifiers, model weights, inference settings, and the historical national CSV has not been established. These reports do not constitute an independently rerunnable training evaluation or certify train/test independence. That lineage needs to be supplied for a final reproducibility release.

## Human review of selected surges

[human_audit_summary.csv](human_audit_summary.csv) transcribes six aggregate counts from *MLEED Validation*, prepared by Idalee Vargas and dated 18 June 2026. The private source HTML is identified by SHA-256 in the provenance record.

Three reviewers assessed selected country-month surges. Categories were divided among reviewers, and observations were chosen to span geographic settings, media environments, and article volumes. **Selection was purposive, not random.** Reviewers checked category assignment, country assignment, and whether the month represented a meaningful surge. Borderline article cases were counted as correct. Sudden-onset and slow-onset disasters were excluded.

The summary records 1,232 correct of 1,481 reviewed articles (83.187%) and 98 valid of 100 selected surges (98%). These are descriptive fractions within the selected sample. They do not estimate population-wide accuracy, recall of unobserved surges, or inter-rater agreement; dividing categories among reviewers does not provide overlapping ratings for agreement analysis.

The 205 event-error flags plus 30 geographic-error flags total 235, whereas 1,481 minus 1,232 gives 249 incorrect cases. The report does not explain the difference of 14 or establish mutually exclusive and exhaustive error types. Treat these categories as incompletely reconciled. The report also describes a minimum of three articles for selected surge candidates; this alone does not reconstruct the stored indicator algorithms.
