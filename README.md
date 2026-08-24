# Machine Learning for Environmental Event Detection (MLEED)

MLEED is a country-month dataset of environmental events and human responses to environmental stress. It is built from multilingual news coverage and spans 69 countries from January 2012 through December 2025.

This repository is the public, pre-publication home for the data and supporting materials associated with the MLEED paper. The manuscript and paper-specific results are intentionally not included at this stage.

## Start here

| Resource | What it contains |
| --- | --- |
| [`data/mleed_country_month_2012_2025.csv`](data/mleed_country_month_2012_2025.csv) | Complete country-month panel: 11,592 rows, 69 countries, 168 months, and 88 columns |
| [`docs/data_dictionary.md`](docs/data_dictionary.md) | Unit of observation, event taxonomy, column families, and interpretation notes |
| [`scripts/build_overview.py`](scripts/build_overview.py) | Portable validation and descriptive-output script |
| [`outputs/data_quality_summary.json`](outputs/data_quality_summary.json) | Machine-readable structural checks and source-file checksum |
| [`outputs/event_distribution.csv`](outputs/event_distribution.csv) | Aggregate distribution of the 16 substantive MLEED event categories |
| [`figures/event_distribution.png`](figures/event_distribution.png) | Descriptive overview generated from the public data |
| [`docs/repository_scope.md`](docs/repository_scope.md) | What is public now, what is withheld, and the publication-release checklist |

## What MLEED measures

MLEED organizes environmental reporting into 16 substantive categories covering:

- environmental hazards: sudden-onset, slow-onset, and human-induced disasters;
- individual responses: displacement, environmental crime, and environmental violence;
- social responses: environmental activism, protests, and corporate initiatives; and
- governmental responses: arrests, cooperation, corruption, initiatives, legal action, legal change, and environmental security.

The distributed file contains raw country-month article-label counts, normalized values, and precomputed surge indicators. Normalized values are stored as proportions of all locally relevant documents in that country-month. Multiply a `*Norm` value by 10,000 to express it as events per 10,000 articles. See the [data dictionary](docs/data_dictionary.md) before analysis.

## Quick start

Create an environment with Python 3.11, install the tested dependencies, and rebuild the public checks and overview:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python scripts/build_overview.py
```

Minimal Python example:

```python
import pandas as pd

data = pd.read_csv(
    "data/mleed_country_month_2012_2025.csv",
    parse_dates=["date"],
)

data["sudden_disasters_per_10k"] = (
    data["sudden-onset environmental disasterNorm"] * 10_000
)
```

## For editors and reviewers

The repository currently provides the aggregate public dataset, documentation, a checksum, and a reproducible descriptive check. It does **not** contain the manuscript, submission PDFs, draft tables, paper-result figures, licensed article text, or third-party datasets.

The source news corpus cannot be redistributed in full because of publisher copyright and licensing restrictions. The public CSV contains aggregate country-month measures and no article text.

Before the archival publication release, the project team plans to add the final paper citation and DOI, an explicit code/data license, and any additional evaluation or reproduction artifacts that can be redistributed. Until a license is added, public availability should not be interpreted as a grant of reuse rights.

## Related resources

- [Interactive MLEED dashboard](https://huggingface.co/spaces/zungru/mlp-mleed-dashboard)
- [Interactive subnational environmental dashboard](https://huggingface.co/spaces/zungru/subnational-env-dashboard)
- [Machine Learning for Peace project](https://web.sas.upenn.edu/mlp-devlab/)
- [Broader MLP data pipeline and documentation](https://github.com/ML4PDevLab/MLP-data-intro)
- [PDRI–DevLab at the University of Pennsylvania](https://pdri-devlab.upenn.edu/)

## Citation and versioning

This is a pre-publication snapshot. The definitive citation, archival DOI, license, and versioned release will be added after publication. For work begun before then, record the repository URL, commit hash, and the SHA-256 value in `outputs/data_quality_summary.json`.
