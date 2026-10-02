# Changelog

## Documentation clarification — 2026-10-02

- Distinguished country-month rows from article-label counts and explained that the screened article pool can retain the category classifier's non-environmental label.
- Clarified the documented numerator and denominator inclusion rules, their historical-provenance limit, and the meanings of the auxiliary count columns. Data, evaluation metrics and executable code are unchanged.

## Submission preparation — 2026-09-29

- Added the upstream binary gate's separate 2×2 aggregate matrix, with exact source hash and verified 421/431 correct classifications.
- Recovered the surge definitions with their existing upstream MIT notice and supplied a standalone comparison script. Two full-window historical inputs reproduce their own indicators on the shared cells, but neither exactly matches the frozen release.

- Preserved the national 2012–2025 CSV exactly: 69 countries, 11,592 rows, 88 columns.
- Added an 88-field schema, country/year coverage, snapshot metadata, a public-file manifest, and checksums.
- Strengthened structural checks and added tested 16-category long-format export code.
- Added six unchanged aggregate classifier reports and a text-free human-audit summary, with arithmetic verification and sample limitations.
- Documented 36 indicator discrepancies and unresolved historical algorithm linkage.
- Clarified reporting-rate units and distinguished deposited coverage from live products.
- Clarified that cross-country document totals count contributions and may repeat international reports.
- Recorded unresolved license, DOI, collection-completeness, and reproducibility requirements.

## Initial public materials — source commit `9f335a2`

National country-month panel, basic dictionary, overview script, descriptive distribution, and project links.
