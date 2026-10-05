# The script reports warnings and errors; it does not change the input files.
from __future__ import annotations

import argparse
from pathlib import Path
import json
import sys

import numpy as np
import pandas as pd


RAW_REQUIRED = {
    "q89", "qn26", "qn27", "qn28", "q88", "qn23", "qn24",
    "q1", "q2", "raceeth", "weight", "stratum", "psu"
}
BINARY_COLUMNS = ["qn26", "qn27", "qn28", "qn23", "qn24"]
GRADE_COLUMN = "q89"


class QAReport:
    def __init__(self) -> None:
        self.checks = []

    def add(self, name: str, status: str, detail: str) -> None:
        self.checks.append({"check": name, "status": status, "detail": detail})

    @property
    def errors(self):
        return [x for x in self.checks if x["status"] == "ERROR"]

    @property
    def warnings(self):
        return [x for x in self.checks if x["status"] == "WARNING"]

    def print(self) -> None:
        for item in self.checks:
            print(f"[{item['status']}] {item['check']}: {item['detail']}")
        print(f"\nChecks: {len(self.checks)} | Errors: {len(self.errors)} | Warnings: {len(self.warnings)}")


def check_raw_data(path: Path, report: QAReport) -> pd.DataFrame | None:
    try:
        df = pd.read_csv(path, low_memory=False)
        df.columns = [str(c).lower() for c in df.columns]
    except Exception as exc:
        report.add("File can be read", "ERROR", str(exc))
        return None

    missing = sorted(RAW_REQUIRED - set(df.columns))
    if missing:
        report.add("Required columns", "ERROR", f"Missing: {missing}")
    else:
        report.add("Required columns", "PASS", f"All {len(RAW_REQUIRED)} required columns are present")

    if len(df) == 0:
        report.add("Row count", "ERROR", "The input file has no rows")
    else:
        report.add("Row count", "PASS", f"Loaded {len(df):,} rows")

    for col in BINARY_COLUMNS:
        if col not in df:
            continue
        observed = set(pd.to_numeric(df[col], errors="coerce").dropna().unique())
        unexpected = sorted(observed - {1, 2})
        status = "ERROR" if unexpected else "PASS"
        report.add(f"{col} response codes", status,
                   f"Observed {sorted(observed)}; expected non-missing codes are 1 and 2")

    if GRADE_COLUMN in df:
        observed = set(pd.to_numeric(df[GRADE_COLUMN], errors="coerce").dropna().unique())
        unexpected = sorted(observed - set(range(1, 8)))
        status = "ERROR" if unexpected else "PASS"
        report.add("q89 grade codes", status,
                   f"Observed {sorted(observed)}; expected codes are 1 through 7")

    if "weight" in df:
        weights = pd.to_numeric(df["weight"], errors="coerce")
        bad = int((weights <= 0).sum())
        missing = int(weights.isna().sum())
        status = "ERROR" if bad else ("WARNING" if missing else "PASS")
        report.add("Student weights", status,
                   f"{bad} non-positive and {missing} missing weights")

    for col in ["psu", "stratum"]:
        if col in df:
            missing = int(df[col].isna().sum())
            status = "WARNING" if missing else "PASS"
            report.add(f"{col} completeness", status,
                       f"{missing} missing values out of {len(df):,} rows")

    for col in ["q1", "q2", "q88"]:
        if col in df:
            values = pd.to_numeric(df[col], errors="coerce")
            report.add(f"{col} numeric conversion", "PASS",
                       f"{values.notna().sum():,} values converted successfully")

    return df


def check_result_file(path: Path, report: QAReport) -> None:
    try:
        result = pd.read_csv(path)
    except Exception as exc:
        report.add(f"Result file {path.name}", "ERROR", str(exc))
        return

    lower = {str(c).lower(): c for c in result.columns}
    numeric_columns = [c for c in result.columns if any(k in str(c).lower() for k in ["or", "prevalence", "weighted", "ci", "p-value", "p_value"])]
    bad_values = []
    for col in numeric_columns:
        values = pd.to_numeric(result[col], errors="coerce")
        if values.notna().any() and np.isinf(values.dropna()).any():
            bad_values.append(str(col))

    if bad_values:
        report.add(f"Result file {path.name}", "ERROR", f"Infinite numeric values in {bad_values}")
    else:
        report.add(f"Result file {path.name}", "PASS", f"Loaded {len(result):,} result rows")

    for key, original in lower.items():
        values = pd.to_numeric(result[original], errors="coerce")
        if "prevalence" in key or "weighted_%" in key:
            invalid = int(((values < 0) | (values > 100)).sum())
            if invalid:
                report.add(f"{path.name} prevalence range", "ERROR", f"{invalid} values outside 0–100")
        if key in {"or", "odds_ratio", "adjusted_or"}:
            invalid = int((values <= 0).sum())
            if invalid:
                report.add(f"{path.name} odds-ratio range", "ERROR", f"{invalid} values are not positive")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate YRBSS inputs and optional exported results.")
    parser.add_argument("raw_file", type=Path, help="Path to the raw yrbs2023.csv file")
    parser.add_argument("--results", type=Path, help="Folder containing exported CSV result files")
    parser.add_argument("--report", type=Path, help="Optional JSON path for the QA report")
    args = parser.parse_args()

    report = QAReport()
    check_raw_data(args.raw_file, report)

    if args.results:
        files = sorted(args.results.glob("*.csv")) if args.results.is_dir() else [args.results]
        if not files:
            report.add("Result files", "WARNING", f"No CSV files found in {args.results}")
        for file in files:
            check_result_file(file, report)

    report.print()
    if args.report:
        args.report.write_text(json.dumps(report.checks, indent=2), encoding="utf-8")
        print(f"Saved QA report to {args.report}")

    return 1 if report.errors else 0


if __name__ == "__main__":
    sys.exit(main())
