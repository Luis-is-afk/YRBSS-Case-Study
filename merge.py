# Merges the two csv files, XXHq.csv & XXHqn.csv into one merged file (yrbs2923.csv)
import pandas as pd

q  = pd.read_csv("XXHq.csv");  qn = pd.read_csv("XXHqn.csv")
q.columns  = q.columns.str.lower();  qn.columns = qn.columns.str.lower()

print(q.shape, qn.shape)                      # same number of rows?
print(set(q.columns) & set(qn.columns))       # shared columns (ID, weight, etc.)
for c in ["weight", "stratum", "psu", "record"]:
    print(c, c in q.columns, c in qn.columns)

key = "record"                                # use whatever shared ID you found
shared = (set(q.columns) & set(qn.columns)) - {key}
merged = q.merge(qn.drop(columns=list(shared)), on=key, how="inner", validate="1:1")
print(merged.shape)                           # should equal len(q)
merged.to_csv("yrbs2023.csv", index=False)