import sys
import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf

# ---- 1. Map roles
VARS = {
    "grades":   "q89",      # self-reported grades (VERIFY)
    "sad":      "qn26",     # persistent sadness/hopelessness
    "consider": "qn27",     # seriously considered suicide
    "plan":     "qn28",     # made a suicide plan
    "sleep":    "q88",      # school-night sleep hours (VERIFY)
    "bully":    "qn23",     # bullied at school (VERIFY)
    "cyber":    "qn24",     # electronically bullied (VERIFY)
    "age":      "q1",
    "sex":      "q2",
    "race":     "raceeth",
    "weight":   "weight",
    "stratum":  "stratum",
    "psu":      "psu",
}
OUTCOMES = ["sad", "consider", "plan"]

# ---- 2. Load & recode ---------------------------------------------------------
def load(path):
    df = pd.read_csv(path, low_memory=False)
    df.columns = [c.lower() for c in df.columns]
    missing = [v for v in VARS.values() if v not in df.columns]
    if missing:
        sys.exit(f"Columns not found in file: {missing}. Fix VARS.")
    d = pd.DataFrame({k: df[v] for k, v in VARS.items()})

    # outcomes: 1=Yes, 2=No -> 1/0
    for o in OUTCOMES + ["bully", "cyber"]:
        d[o] = d[o].map({1: 1, 2: 0})

    # grades: 1=A ... 5=F; 6 ("none of these") and 7 ("not sure") -> missing
    d["grades"] = d["grades"].where(d["grades"].between(1, 5))
    labels = {1: "A", 2: "B", 3: "C", 4: "D", 5: "F"}
    d["grades_cat"] = pd.Categorical(d["grades"].map(labels),
                                     categories=["A", "B", "C", "D", "F"])
    # sleep: 1 = <=4h ... 7 = >=10h (ordinal code; VERIFY)
    d["sleep"] = d["sleep"].where(d["sleep"].between(1, 7))
    d["sex"] = d["sex"].map({1: "Female", 2: "Male"})
    d["age"] = d["age"].where(d["age"].between(1, 7))
    d["race"] = d["race"].astype("category")
    d["weight"] = d["weight"].astype(float)
    return d

# ---- 3. Weighted prevalence by grade category ---------------------------------
def weighted_prev(d, outcome):
    sub = d.dropna(subset=[outcome, "grades_cat", "weight"])
    rows = []
    for g, grp in sub.groupby("grades_cat", observed=True):
        p = np.average(grp[outcome], weights=grp["weight"])
        rows.append({"grades": g, "n": len(grp), "weighted_%": round(100 * p, 1)})
    return pd.DataFrame(rows)

# ---- 4. Weighted logistic regression -> odds ratios ---------------------------
def odds_ratios(d, outcome, adjusted=True):
    cols = [outcome, "grades_cat", "weight", "psu"]
    rhs = "C(grades_cat, Treatment('A'))"
    if adjusted:
        rhs += " + C(sex) + age + C(race) + sleep + bully + cyber"
        cols += ["sex", "age", "race", "sleep", "bully", "cyber"]
    sub = d.dropna(subset=cols)
    m = smf.glm(f"{outcome} ~ {rhs}", data=sub, family=sm.families.Binomial(),
                freq_weights=sub["weight"]).fit(
        cov_type="cluster", cov_kwds={"groups": sub["psu"]})
    ci = np.exp(m.conf_int())
    out = pd.DataFrame({"OR": np.exp(m.params), "CI_low": ci[0],
                        "CI_high": ci[1], "p": m.pvalues}).round(3)
    return out[out.index.str.contains("grades_cat")], int(m.nobs)

if __name__ == "__main__":
    d = load(sys.argv[1])
    for o in OUTCOMES:
        print(f"\n=== {o}: weighted prevalence by grades ===")
        print(weighted_prev(d, o).to_string(index=False))
        for adj in (False, True):
            res, n = odds_ratios(d, o, adjusted=adj)
            print(f"\n{o} odds ratios vs. mostly A's "
                  f"({'adjusted' if adj else 'unadjusted'}, n={n})")
            print(res.to_string())
