# Replication package: Transparency in Indian Agricultural Economics Research

This repository contains the data and code to reproduce the empirical exercise reported in:

> Aditya, K.S., Surendran-Padmaja, S., Qureshi, N., Jha, G.K., and Batla, S. (2026). *Advancing Transparency and Reproducibility of Agricultural Economics Research in India.*

The exercise scores 44 papers (27 from Agricultural Economics Research Review, 17 from Indian Journal of Agricultural Economics) against a 20-item transparency-in-reporting checklist, using four independent raters per paper, and reports the per-criterion compliance rate by journal.

We share this package as a small step toward the practices the paper advocates.

## Repository structure

```
.
├── data/
│   └── scoring_data.xlsx                         Raw scores, codebook, paper metadata
├── scripts/
│   └── compute_compliance.py                     Reproduces the figure and rate table
├── figures/
│   ├── compliance_rate_by_criterion.png          Output: side-by-side compliance chart
│   └── compliance_rate_by_criterion.csv          Output: per-criterion rates by journal
├── requirements.txt                              Python dependencies
├── LICENSE                                       MIT license
└── README.md                                     This file
```

## Data

The file `data/scoring_data.xlsx` is the canonical input. It contains the following sheets:

| Sheet | Contents |
| --- | --- |
| `README` | Description of the workbook, sample size, coding scheme |
| `criterion_labels` | Codebook mapping `C1..C20` to short labels and full descriptions |
| `papers` | Paper-level metadata (`paper_id`, `journal`, `study_notes`) |
| `scores_long` | Tidy long format. One row per paper, scorer, criterion. 3,520 rows in total (44 papers x 4 scorers x 20 criteria) |
| `scores_Human_1_wide` | Wide format for Human rater 1 |
| `scores_Human_2_wide` | Wide format for Human rater 2 |
| `scores_AI_wide` | Wide format for the initial automated AI rater |
| `scores_Claude_wide` | Wide format for the Claude rater |

Each criterion is coded as a binary variable (1 = met, 0 = not met). A small number of cells are blank, indicating that the AI rater could not assess that criterion for a given paper. These are treated as missing in the compliance-rate computation (see below).

The 20 criteria are listed in `criterion_labels` and follow the transparency checklist in the paper.

## Method: how the compliance rate is computed

For a given criterion `c` and journal `j`:

1. For each paper `i` in journal `j`, take the mean of the 4 scorers' values on criterion `c`, ignoring missing entries (`nanmean`). This gives a per-paper compliance fraction in `[0, 1]`.
2. Average that fraction across all papers in journal `j`.
3. Multiply by 100 to express as a percentage.

The script does not hardcode any rates. It recomputes them from `scores_long` every run.

## How to reproduce

### 1. Set up Python

A recent Python (3.9 or newer) is required. From the repository root:

```bash
python -m venv .venv
source .venv/bin/activate          # on Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Run the script

```bash
python scripts/compute_compliance.py
```

This reads `data/scoring_data.xlsx`, computes the per-journal per-criterion compliance rates, and writes:

* `figures/compliance_rate_by_criterion.png` (the side-by-side chart shown in the paper),
* `figures/compliance_rate_by_criterion.csv` (the corresponding numeric table).

The console output prints the full rate table and the sample sizes by journal.

### 3. Expected output

```
N papers: AERR = 27, IJAE = 17, Total = 44

Compliance rates (%):
journal     AERR   IJAE
criterion
C1         92.59  92.65
C2         99.07  91.18
...
C19         0.00   0.00
C20         0.00   0.00
```

## Citation

If you use this data or code, please cite the paper above and link to this repository.

## License

The code in this repository is released under the MIT License (see `LICENSE`). The data is shared for replication and academic use; please cite the paper when using it.

## Contact

For questions or corrections, please open an issue on the repository or contact the corresponding author.
