import pandas as pd

df = pd.read_csv("data/ground_truth/pii_annotations.csv")

print("Total PII entities:", len(df))

print("\nBy entity type:")
print(df["entity_type"].value_counts())

print("\nBy tenant (derived from filename):")
df["tenant"] = df["file_name"].str.split("_").str[0]
print(df["tenant"].value_counts())

print("\nBy regulation:")
print(df["regulation"].value_counts())