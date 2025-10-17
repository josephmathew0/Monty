import pandas as pd
df = pd.read_excel("project_data/oesm24all/all_data_M_2024.xlsx", usecols=["OCC_TITLE"])
print(df["OCC_TITLE"].dropna().unique()[:50])
