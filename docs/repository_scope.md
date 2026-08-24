# Repository scope and release plan

This document separates the materials suitable for the public pre-publication repository from files that should remain in the private submission workspace.

## Included now

| Material | Reason for inclusion |
| --- | --- |
| Canonical country-month CSV | Core public research output; aggregate data with no article text |
| Data dictionary and taxonomy | Makes the schema interpretable without exposing the manuscript |
| Structural validation and overview script | Lets readers verify the panel and rebuild neutral descriptive outputs |
| Data-quality summary and checksum | Supports provenance and version tracking |
| One descriptive distribution table and figure | Gives readers a compact, non-paper-specific orientation to the data |
| Links to project sites, dashboards, and the broader MLP pipeline | Connects the release to maintained project context and tools |

## Intentionally not included in this pre-publication package

| Material | Reason for exclusion |
| --- | --- |
| Manuscript source and submission PDF | The paper is under review and is not yet intended for public distribution |
| Draft supplementary information | Part of the private submission package |
| Paper-specific result figures and tables | Avoids publishing the paper’s results ahead of the paper |
| Validation HTML and working review files | These may contain review context or intermediate artifacts and need a separate release decision |
| Duplicate, superseded, and renamed CSV snapshots | Prevents ambiguity about the canonical data file |
| ZIP archives and operating-system metadata | Redundant or generated clutter |
| Full news-article text | Cannot be redistributed because of publisher copyright and licensing restrictions |
| Third-party EM-DAT, IDMC, and U.S. government data | Users should obtain these from their providers unless redistribution rights are confirmed |
| Analyses requiring unavailable private inputs | A public script should run from the files actually distributed with it |

## Checklist for the publication release

- Confirm the canonical data snapshot and create a versioned GitHub release.
- Add the final paper citation and archival DOI.
- Add explicit licenses for code and data after the project team approves them.
- Add paper-reproduction code with a complete input manifest and provider links.
- Add public-safe model evaluation and validation artifacts, with clear sample definitions.
- Add a changelog describing changes from this pre-publication snapshot.
- Archive the release in a DOI-granting repository and record checksums.
