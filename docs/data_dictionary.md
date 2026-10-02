# MLEED country-month data dictionary

## Dataset summary

- File: `data/mleed_country_month_2012_2025.csv`
- Unit of observation: country-month
- Coverage: January 2012 through December 2025
- Countries: 69
- Rows: 11,592 (69 countries × 168 months)
- Columns: 88
- Date format: `YYYY-MM-DD`, using the first day of each month
- Missing cells in this release: none

The panel is balanced: every country has one observation for every month in the coverage period.

Each row represents one country-month. Within that row, a raw category count records article-label assignments, not distinct incidents. An article can receive a primary and a secondary label. Document counts refer to contributions to a country-month; an international report may contribute to multiple countries, so cross-country sums are not verified counts of unique corpus documents.

This describes the deposited file, not a certification that every source was collected. The exact 69 country names and all 88 fields are recorded in [metadata/schema.json](../metadata/schema.json). Country and year summaries appear in [outputs/country_coverage.csv](../outputs/country_coverage.csv) and [outputs/year_coverage.csv](../outputs/year_coverage.csv).

## Identifier and coverage columns

| Column | Type | Description |
| --- | --- | --- |
| `country` | string | Country name used by the MLEED release |
| `date` | date | First day of the observation month |
| `year` | integer | Calendar year |
| `month` | integer | Calendar month, 1–12 |
| `total_articles` | integer | Articles retained after environmental-relevance screening and with a category-classification record; this screened pool can include the second model's `-999` label |
| `total_from_source` | integer | The same screened article pool aggregated across the included sources; identical to `total_articles` in this release |
| `total_label_events` | integer | Sum of all 20 raw label columns, including auxiliary fields; an article may contribute primary and secondary labels |
| `total_local_docs` | integer | All locally relevant documents in the country-month and the denominator for normalized measures |

In the documented July 2026 aggregation routine, the denominator includes all records meeting the inclusion, source and country rules, without an environmental-classification filter. The screened article pool additionally requires `environmental_binary.result` to be `Yes` and an existing `env_classifier` record. Its primary and secondary labels are counted without removing the second model's non-environmental (`-999`) label. These totals therefore do not count independently verified environmental articles. The documented routine explains these field meanings; its exact version has not been linked to the historical CSV, as noted in [repository scope](repository_scope.md).

## Substantive event taxonomy

The paper-level taxonomy contains 16 categories. The data keeps lethal and nonlethal environmental violence separate; pool those two columns when reproducing the 16-category taxonomy.

| Family | Public data column(s) | Interpretation |
| --- | --- | --- |
| Environmental hazard | `sudden-onset environmental disaster` | Rapid-onset events such as floods, storms, earthquakes, or wildfires |
| Environmental hazard | `slow-onset environmental disaster` | Gradual environmental stress such as drought, desertification, or salinization |
| Environmental hazard | `human-induced disaster` | Environmental harm caused by human or industrial activity |
| Individual response | `displacement` | Environmentally linked displacement or migration reporting |
| Individual response | `environmental crime` | Illegal activity involving natural resources or environmental harm |
| Individual response | `lethal environmental violence`; `nonlethal environmental violence` | Environmentally linked violence, separated by lethality in the data and pooled as “environmental violence” in the 16-category taxonomy |
| Social response | `environmental activism` | Civic or community environmental organizing outside the protest category |
| Social response | `environmental protests` | Collective protest over environmental issues |
| Social response | `environmental corporate initiatives` | Environmental action or adaptation led by firms |
| Governmental response | `environmental arrest` | Arrests connected to environmental activity, crime, or enforcement |
| Governmental response | `environmental cooperation` | Environmental cooperation among public or public-private actors |
| Governmental response | `environmental corruption` | Corruption connected to environmental governance or resources |
| Governmental response | `environmental government initiatives` | Government-led environmental programs or operational initiatives |
| Governmental response | `environmental legal action` | Enforcement, litigation, or other action under existing law |
| Governmental response | `environmental legal change` | Adoption or revision of environmental laws or regulations |
| Governmental response | `environmental security` | Use of security institutions or security policy for environmental purposes |

## Auxiliary classifier fields

The data also contains three classifier bookkeeping categories:

- `environmental opinion`: environmental opinion content
- `environmental -999`: environmental content outside the named categories
- `-999`: the category classifier's non-environmental label

These are not part of the 16 substantive categories and should normally be excluded from substantive event totals, figures, and models. They are retained so that the aggregate table remains traceable to the classification output. The two names containing `-999` identify count columns, not missing-value codes.

## Repeated column families

Each raw event or auxiliary column is followed by derived fields with the same base name.

| Pattern | Type | Interpretation |
| --- | --- | --- |
| `<event>` | nonnegative integer | Raw number of assigned article labels in the country-month, not unique physical events |
| `<event>Norm` | float | Raw count divided by `total_local_docs`; multiply by 10,000 for a rate per 10,000 locally relevant documents |
| `<event>NormShock` | binary integer | Precomputed indicator for an unusually high normalized value in that country-event series |
| `<event>NormShockCountGt3` | binary integer | Precomputed surge indicator with an additional count-based screen from the production snapshot |

A recovered production routine reproduces two later source inputs on their historical overlap, but the exact input and execution state for this snapshot's indicators remain unresolved; see [surge reconstruction](surge_reconstruction.md). The fields are not regenerated by `scripts/build_overview.py`. There are 36 cells across 14 label series where `NormShockCountGt3` differs from `(NormShock == 1) and (raw_count > 3)`; see [outputs/indicator_diagnostics.csv](../outputs/indicator_diagnostics.csv). This comparison diagnoses the stored fields separately from candidate reconstruction. The stored values remain unchanged. Analysts should use independently verified counts or normalized measures, or define a new surge rule transparently.

## Recommended analytical conventions

1. Parse `date` as a monthly date and verify uniqueness on `country` + `date`.
2. Use raw event columns for counts and `*Norm` columns for coverage-adjusted comparisons.
3. For label counts per 10,000 documents, multiply stored `*Norm` proportions by 10,000. Do not describe these as counts of unique events or people.
4. Pool lethal and nonlethal environmental violence if using the paper’s 16-category taxonomy.
5. Exclude the three auxiliary classifier fields from substantive event summaries.
6. Treat the data as measures of media coverage and event salience, not direct estimates of population incidence.
7. Preserve the source file and record its SHA-256 checksum when creating transformed analysis data.
8. Treat a zero as no recorded labels in the included corpus, not proof of no environmental event. Positive denominators range from 2 to 103,247 documents per country-month.
9. Aggregate rates by summing matching numerators and denominators before division. Do not sum denominators across repeated label categories in a long-format export.
