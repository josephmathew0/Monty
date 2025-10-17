import pandas as pd

df = pd.read_excel(
    "project_data/oesm24all/all_data_M_2024.xlsx",
    usecols=["AREA_TITLE", "OCC_TITLE", "TOT_EMP"]
)

# Only rows with 'Chief Executives'
df = df[df["OCC_TITLE"].str.contains("Chief Executives", case=False, na=False)]

print("\n🔹 Found rows for Chief Executives:")
print(df.head(20))
print("\nUnique AREA_TITLEs:", df["AREA_TITLE"].unique())
print("\nTotal rows:", len(df))
