from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent
DATA_PATH = ROOT / "data" / "utility_billing.csv"
OUTPUT_DIR = ROOT / "output"
OUTPUT_DIR.mkdir(exist_ok=True)


def load_and_clean_data(path):
    df = pd.read_csv(path)
    df["billing_month"] = pd.to_datetime(df["billing_month"], errors="coerce")

    required = ["account_id", "billing_month", "usage_kwh", "billed_amount"]
    df = df.dropna(subset=required)

    # Keep one row per account-month.
    df = df.drop_duplicates(subset=["account_id", "billing_month"], keep="first")

    return df


def detect_anomalies(df):
    # Estimate the typical utility rate from all valid records.
    rates = df.loc[df["usage_kwh"] > 0, "billed_amount"] / df.loc[df["usage_kwh"] > 0, "usage_kwh"]
    avg_rate = rates.mean()

    df = df.copy()
    df["expected_amount"] = df["usage_kwh"] * avg_rate
    df["deviation_amount"] = df["billed_amount"] - df["expected_amount"]
    df["deviation_pct"] = (
        df["deviation_amount"].abs() / df["expected_amount"].replace(0, np.nan) * 100
    )

    # Flag records more than 2 standard deviations from expected billing.
    std_dev = df["deviation_amount"].std()
    threshold = 2 * std_dev
    df["is_anomaly"] = df["deviation_amount"].abs() > threshold

    return df, avg_rate, threshold


def save_outputs(df):
    flagged = df[df["is_anomaly"]].copy()
    flagged = flagged.sort_values("deviation_amount", key=lambda s: s.abs(), ascending=False)

    summary = flagged[
        [
            "account_id",
            "billing_month",
            "usage_kwh",
            "billed_amount",
            "expected_amount",
            "deviation_amount",
            "deviation_pct",
        ]
    ].copy()

    summary.to_csv(OUTPUT_DIR / "flagged_anomalies.csv", index=False)

    # Simple chart: number of normal vs flagged billing records.
    counts = df["is_anomaly"].map({False: "Normal", True: "Flagged"}).value_counts()
    plt.figure(figsize=(7, 4.5))
    counts.reindex(["Normal", "Flagged"], fill_value=0).plot(kind="bar")
    plt.title("Utility Billing Records: Normal vs Flagged")
    plt.xlabel("")
    plt.ylabel("Number of records")
    plt.xticks(rotation=0)
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "flagged_vs_normal.png", dpi=150)
    plt.close()


def main():
    df = load_and_clean_data(DATA_PATH)
    results, avg_rate, threshold = detect_anomalies(df)
    save_outputs(results)

    flagged = results[results["is_anomaly"]]
    flagged_pct = len(flagged) / len(results) * 100 if len(results) else 0
    avg_deviation = flagged["deviation_amount"].abs().mean() if len(flagged) else 0

    print("\nUtility Billing Anomaly Detection")
    print("---------------------------------")
    print(f"Clean billing records: {len(results)}")
    print(f"Average cost per kWh: ${avg_rate:.4f}")
    print(f"Anomaly threshold: ${threshold:.2f}")
    print(f"Records flagged: {len(flagged)} ({flagged_pct:.2f}%)")
    print(f"Average absolute deviation: ${avg_deviation:.2f}")

    print("\nFlagged anomalies:")
    if flagged.empty:
        print("No anomalies found.")
    else:
        print(
            flagged[
                [
                    "account_id",
                    "billing_month",
                    "billed_amount",
                    "expected_amount",
                    "deviation_amount",
                    "deviation_pct",
                ]
            ].to_string(index=False)
        )

    print(f"\nSaved: {OUTPUT_DIR / 'flagged_anomalies.csv'}")
    print(f"Saved: {OUTPUT_DIR / 'flagged_vs_normal.png'}")


if __name__ == "__main__":
    main()
