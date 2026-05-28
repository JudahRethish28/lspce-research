# scripts/add_tenant_to_annotations.py
import pandas as pd

df = pd.read_csv("data/ground_truth/pii_annotations.csv")
df["tenant_id"] = df["file_name"].str.split("_log_").str[0]
df.to_csv("data/ground_truth/pii_annotations.csv", index=False)
print("Added tenant_id column.")
print(df["tenant_id"].value_counts())