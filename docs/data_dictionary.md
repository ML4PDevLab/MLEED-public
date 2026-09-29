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

Document counts refer to contributions to a country-month. An international report may contribute to multiple countries, so cross-country sums are not verified counts of unique corpus documents.

This describes the deposited file, not a certification that every source was collected. The exact 69 country names and all 88 fields are recorded in [metadata/schema.json](../metadata/schema.json). Country and year summaries appear in [outputs/country_coverage.csv](../outputs/country_coverage.csv) and [outputs/year_coverage.csv](../outputs/year_coverage.csv).

## Identifier and coverage columns

| Column | Type | Description |
| --- | --- | --- |
| `country` | string | Country name used by the MLEED release |
| `date` | date | First day of the observation month |
| `year` | integer | Calendar year |
| `month` | integer | Calendar month, 1–12 |
| `total_articles` | integer | Environmental documents included in the country-month numerator pool |
| `total_from_source` | integer | Environmental documents aggregated across the included sources; identical to `total_articles` in this release |
| `total_label_events` | integer | Sum of all 20 raw label columns, including auxiliary fields; an article may contribute primary and secondary labels |
| `total_local_docs` | integer | All locally relevant documents in the country-month and the denominator for normalized measures |

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

- `environmental opinion`
- `environmental -999`
- `-999`

These are not part of the 16 substantive categories and should normally be excluded from substantive event totals, figures, and models. They are retained so that the aggregate table remains traceable to the classification output.

## Repeated column families

Each raw event or auxiliary column is followed by derived fields with the same base name.

| Pattern | Type | Interpretation |
| --- | --- | --- |
| `<event>` | nonnegative integer | Raw number of assigned article labels in the country-month, not unique physical events |
| `<event>Norm` | float | Raw count divided by `total_local_docs`; multiply by 10,000 for a rate per 10,000 locally relevant documents |
| `<event>NormShock` | binary integer | Precomputed indicator for an unusually high normalized value in that country-event series |
| `<event>NormShockCountGt3` | binary integer | Precomputed surge indicator with an additional count-based screen from the production snapshot |

The historical production routine and fitted state that created the two shock indicators have not been linked to this snapshot. They are distributed as precomputed fields and are not regenerated by `scripts/build_overview.py`. There are 36 cells across 14 label series where `NormShockCountGt3` differs from `(NormShock == 1) and (raw_count > 3)`; see [outputs/indicator_diagnostics.csv](../outputs/indicator_diagnostics.csv). This comparison is a diagnostic of the literal suffix interpretation, not an asserted reconstruction of the algorithm. The stored values remain unchanged. Analysts should use independently verified counts or normalized measures, or define a new surge rule transparently.

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
