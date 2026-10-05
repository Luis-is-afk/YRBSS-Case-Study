"""
YRBSS Table Exporter: Generates Markdown & CSV report tables.
Run: python export_tables.py yrbs2023.csv
"""
import os
import sys
import pandas as pd
from analysis import load, weighted_prev, odds_ratios, OUTCOMES

def export_all_tables(data_path: str, output_dir: str = "exports"):
    """
    Executes YRBSS statistical models and exports formatted tables 
    to Markdown and CSV formats for documentation and reporting.
    """
    os.makedirs(output_dir, exist_ok=True)
    d = load(data_path)
    
    md_report = []
    md_report.append("# CDC YRBSS 2023 Statistical Analysis Summary\n")
    md_report.append("This document contains weighted prevalence rates and logistic regression odds ratios examining academic performance vs. mental health outcomes.\n")

    outcome_labels = {
        "sad": "Persistent Sadness / Hopelessness (2+ Weeks)",
        "consider": "Seriously Considered Suicide",
        "plan": "Made a Suicide Plan"
    }

    for o in OUTCOMES:
        outcome_title = outcome_labels.get(o, o.upper())
        md_report.append(f"## {outcome_title}\n")
        
        # 1. Weighted Prevalence Table
        prev_df = weighted_prev(d, o)
        prev_df.rename(columns={
            "grades": "Academic Grades",
            "n": "Sample Size (n)",
            "weighted_%": "Weighted Prevalence (%)"
        }, inplace=True)
        
        # Save CSV
        prev_df.to_csv(os.path.join(output_dir, f"{o}_prevalence.csv"), index=False)
        
        md_report.append("### Weighted Prevalence by Grade Category")
        md_report.append(prev_df.to_markdown(index=False))
        md_report.append("\n")

        # 2. Logistic Regression Odds Ratios (Unadjusted vs Adjusted)
        res_unadj, n_unadj = odds_ratios(d, o, adjusted=False)
        res_adj, n_adj = odds_ratios(d, o, adjusted=True)

        # Reformat row labels
        grade_map = {
            "C(grades_cat, Treatment('A'))[T.B]": "Mostly B's vs A's",
            "C(grades_cat, Treatment('A'))[T.C]": "Mostly C's vs A's",
            "C(grades_cat, Treatment('A'))[T.D]": "Mostly D's vs A's",
            "C(grades_cat, Treatment('A'))[T.F]": "Mostly F's vs A's"
        }

        # Combine Unadjusted and Adjusted into a side-by-side comparison table
        combined = pd.DataFrame({
            "Grade Comparison": [grade_map.get(idx, idx) for idx in res_unadj.index],
            "Unadjusted OR": res_unadj["OR"].values,
            "Unadjusted 95% CI": [f"({l:.2f}, {h:.2f})" for l, h in zip(res_unadj["CI_low"], res_unadj["CI_high"])],
            "Adjusted OR": res_adj["OR"].values,
            "Adjusted 95% CI": [f"({l:.2f}, {h:.2f})" for l, h in zip(res_adj["CI_low"], res_adj["CI_high"])],
            "p-value": res_adj["p"].values
        })

        # Save CSV
        combined.to_csv(os.path.join(output_dir, f"{o}_odds_ratios.csv"), index=False)

        md_report.append(f"### Multivariable Logistic Regression Odds Ratios (n = {n_adj})")
        md_report.append("*Adjusted for sex, age, race/ethnicity, sleep duration, school bullying, and cyberbullying.*")
        md_report.append(combined.to_markdown(index=False))
        md_report.append("\n---\n")

    # Write compiled Markdown file
    md_filepath = os.path.join(output_dir, "statistical_summary.md")
    with open(md_filepath, "w", encoding="utf-8") as f:
        f.write("\n".join(md_report))

    print(f"Successfully exported tables to '{output_dir}/' folder:")
    print(f" - Main Markdown Report: {md_filepath}")
    print(" - CSV files for each outcome created.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("Usage: python export_tables.py <path_to_yrbs_csv>")
    export_all_tables(sys.argv[1])