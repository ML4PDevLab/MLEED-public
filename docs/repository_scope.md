# Release scope

The current snapshot contains monthly country summaries for 71 countries from January 2012 through December 2025. Its counts, normalized values and surge fields are extracted from the pinned October 13, 2026 public export. The [source record](../metadata/source_snapshot_71_20261018.json) gives the extraction, hashes and changes from the earlier 69-country version.

## Available materials

| Material | Contents |
| --- | --- |
| Country summaries | 11,928 rows and 88 fields; every country has 168 months |
| Documentation | Country names, field definitions, reuse examples and source records |
| Coverage summaries | Country/year reporting volumes and category distribution |
| Structural checks | Schema, dates, keys, counts, denominator identities and indicator rules |
| Surge reproduction | Exact match for 238,560 cells per family from the pinned complete source |
| Classifier evidence | Unchanged 431-case matrices, including the binary gate |
| Human review | Unchanged summary of 1,481 reviewed articles and 100 selected surges |
| File identity | Version metadata, manifest and SHA-256 checksums |

The earlier data and audit remain at [commit `81c30ac`](https://github.com/ML4PDevLab/MLEED-public/tree/81c30acb56d9d05779c92cb583c04b730b39c680). Current evaluation reports are historical evidence rather than a new validation sample for the 71-country update.

The package contains aggregates and code that checks and transforms them. Article text, individual predictions, credentials, database dumps and third-party benchmark data are excluded. The code does not rerun collection, translation, training, classification or geographic extraction. The regional/local dashboard provides a separate geographic product with its own counts and inclusion rules.

## Remaining deposit items

- Complete the known Libya processing cohort and document any resulting data revision; the present snapshot retains the published values and records the issue in its source metadata.
- Record the extraction, model, source-inclusion and geographic versions used before the country aggregates; exact surge reproduction establishes the indicator calculation, not every earlier processing stage.
- Resolve classifier split/model linkage and the human review's incomplete error accounting, as described in the [validation notes](../validation/README.md).
- Assign authorized aggregate-data and original-code licenses, archive the approved version with a persistent identifier, and cite it in the paper. The copied surge definitions already carry their upstream MIT notice.

Licenses and DOI remain `null` in metadata until assigned. A balanced monthly file establishes its structure; source collection completeness requires separate evidence.
