# Utility Billing Anomaly Detection

A small Python project that identifies unusual electricity billing records by comparing actual charges with an expected charge based on typical cost per kWh.

## Goal

Help a utility team quickly find billing records that look unusually high or low compared with normal usage-based billing.

## Data

The project uses a **synthetic dataset** so it can run without a Kaggle download or API key.

- 250 customer accounts
- 4 monthly billing periods
- Columns: `account_id`, `billing_month`, `usage_kwh`, `billed_amount`
- A few missing values, duplicate account-month rows, and intentionally unusual bills are included to test the workflow.

## Method

1. Load the CSV with pandas.
2. Convert the billing month to a date.
3. Remove rows missing required billing values.
4. Remove duplicate `account_id` + `billing_month` entries.
5. Calculate the average historical cost per kWh.
6. Compute expected billing as `usage_kwh × average_cost_per_kwh`.
7. Flag records where the absolute difference between actual and expected billing is greater than **2 standard deviations**.
8. Save a summary CSV and a simple bar chart.

## Findings from the included dataset

- Clean billing records: **986**
- Average cost per kWh: **$0.1795**
- Records flagged: **24 (2.43%)**
- Average absolute deviation among flagged records: **$101.46**

The flagged records are the best candidates for manual billing review. This is a simple screening model, not proof that a bill is incorrect.

## Run locally

```bash
python -m pip install -r requirements.txt
python detect_anomalies.py
```

Outputs are written to the `output/` folder:

- `flagged_anomalies.csv` — summary table of suspicious records
- `flagged_vs_normal.png` — normal vs flagged record count

## Project structure

```text
utility_billing_anomaly_detection/
├── data/
│   └── utility_billing.csv
├── output/
│   ├── flagged_anomalies.csv
│   └── flagged_vs_normal.png
├── detect_anomalies.py
├── requirements.txt
└── README.md
```
