import pandas as pd

df = pd.read_csv("data/ground_truth/pii_annotations.csv")

print("=== DATASET STATISTICS ===")
print(f"Total annotation rows: {len(df)}")
print(f"Unique files annotated: {df['file_name'].nunique()}")
print()
print("=== BY ENTITY TYPE ===")
print(df['entity_type'].value_counts())
print()
print("=== BY TENANT ===")
df['tenant'] = df['file_name'].str.split('_log_').str[0]
print(df['tenant'].value_counts())
print()
print("=== SAMPLE ROWS ===")
print(df.groupby('entity_type').first()[['entity_text','file_name']])