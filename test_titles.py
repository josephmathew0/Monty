import pandas as pd

# 1. Load the O*NET Education/Training/Experience file
df = pd.read_excel("project_data/ETE.xlsx")

# 2. Inspect available element names
print("Unique Element Names:")
print(df["Element Name"].unique()[:20])

# 3. Filter for entries that represent *education level* categories
#    Sometimes appears as "Percent responding that this level is required"
edu_df = df[df["Element Name"].str.contains("education", case=False, na=False)]

# 4. Keep relevant columns
keep_cols = ["O*NET-SOC Code", "Title", "Element Name", "Data Value"]
edu_df = edu_df[keep_cols]

# 5. Pivot table to get education categories as columns
pivot_df = edu_df.pivot_table(
    index=["O*NET-SOC Code", "Title"],
    columns="Element Name",
    values="Data Value",
    aggfunc="mean"
).reset_index()

# 6. Save to project_data folder
pivot_df.to_csv("project_data/education_levels_distribution.csv", index=False)
print(f"✅ Saved project_data/education_levels_distribution.csv with {len(pivot_df)} rows")
