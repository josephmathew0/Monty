import pandas as pd

df = pd.read_excel(
    "project_data/oesm24all/all_data_M_2024.xlsx",
    usecols=["AREA_TITLE", "OCC_TITLE"]
)
df = df[df["AREA_TITLE"].str.contains("state", case=False, na=False)]

print("\n✅ Total statewide rows:", len(df))
print("\n🔹 Sample OCC_TITLE values:")
print(df["OCC_TITLE"].drop_duplicates().sort_values().head(50).to_list())

print("\n🔍 Titles containing 'chief':")
print(df[df["OCC_TITLE"].str.contains("chief", case=False, na=False)]["OCC_TITLE"].unique())
