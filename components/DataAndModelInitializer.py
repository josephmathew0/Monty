<<<<<<< HEAD
import pandas as pd
import functools
from sentence_transformers import SentenceTransformer
=======
# components/DataAndModelInitializer.py

import pandas as pd
import os
from sentence_transformers import SentenceTransformer
import functools

>>>>>>> 25283421 (🚀 Rebuilt Monty project with new architecture and parser)

class DataAndModelInitializer:
    def __init__(self):
        self.model = None
        self.job_df = None
        self.geo_df = None

<<<<<<< HEAD
    # ---------------------------
    # Model loader
    # ---------------------------
    # def load_model(self):
    #     self.model = SentenceTransformer('all-MiniLM-L6-v2')
    #     return self.model

    def load_model(self):
        if self.model is None:
            print("🧠 Loading SentenceTransformer model on demand...")
            self.model = SentenceTransformer('paraphrase-MiniLM-L3-v2')
        return self.model


    # ---------------------------
    # Job-level dataset (national)
    # ---------------------------
    def load_job_data(self):
        try:
            df = pd.read_excel('project_data/oesm23nat/national_M2023_dl.xlsx')
            keep_cols = ['OCC_TITLE', 'A_MEAN', 'A_MEDIAN', 'H_MEAN', 'TOT_EMP']
            df = df[keep_cols].dropna(subset=['OCC_TITLE']).drop_duplicates(subset=['OCC_TITLE'])
            df = df.rename(columns={'OCC_TITLE': 'Occupation'})

            for col in ['A_MEAN', 'A_MEDIAN', 'H_MEAN', 'TOT_EMP']:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

            df['Description'] = df['Occupation']
            return df[['Occupation', 'Description', 'A_MEAN', 'A_MEDIAN', 'H_MEAN', 'TOT_EMP']]
        except Exception as e:
            print("Error loading job dataset:", e)
            return pd.DataFrame(columns=['Occupation','Description','A_MEAN','A_MEDIAN','H_MEAN','TOT_EMP'])

    # ---------------------------
    # Geographic dataset (state-level)
    # ---------------------------
    @functools.lru_cache(maxsize=1)
    def _read_geo_file(self):
        """Load minimal geographic dataset efficiently (cached)."""
        print("📊 Loading lightweight geographic dataset (cached)…")
        # df = pd.read_excel(
        #     "project_data/oesm24all/all_data_M_2024.xlsx",
        #     usecols=["AREA_TITLE", "OCC_TITLE", "TOT_EMP", "H_MEAN"],
        #     engine="openpyxl",
        #     dtype={
        #         "AREA_TITLE": "string",
        #         "OCC_TITLE": "string",
        #         "TOT_EMP": "float32",
        #         "H_MEAN": "float32"
        #     }

        # Load only first 100000 rows (to fit free-tier memory)
        df = pd.read_excel(
            "project_data/oesm24all/all_data_M_2024.xlsx",
            usecols=["AREA_TITLE", "OCC_TITLE", "TOT_EMP", "H_MEAN"],
            nrows=100000,  # 👈 limit rows
            engine="openpyxl",
            dtype={
                "AREA_TITLE": "string",
                "OCC_TITLE": "string",
                "TOT_EMP": "float32",
                "H_MEAN": "float32"
            }
        ).dropna(subset=["OCC_TITLE", "AREA_TITLE"])
        print(f"✅ Geographic base dataset loaded: {len(df)} rows")
        return df

    def load_geographic_job_data(self, occupation_filter=None):
        """Filter and return geographic employment data for the given occupation."""
        try:
            df = self._read_geo_file()

            # State totals only
            state_list = [
=======
    def load_model(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        return self.model

    def load_job_data(self):
        try:
            df = pd.read_excel('project_data/oesm23nat/national_M2023_dl.xlsx')

            # Keep important columns
            keep_cols = ['OCC_TITLE', 'A_MEAN', 'A_MEDIAN', 'H_MEAN', 'TOT_EMP']
            df = df[keep_cols].dropna(subset=['OCC_TITLE']).drop_duplicates(subset=['OCC_TITLE'])

            # Rename for consistency
            df = df.rename(columns={'OCC_TITLE': 'Occupation'})

            # Fallback: fill missing numeric values
            for col in ['A_MEAN', 'A_MEDIAN', 'H_MEAN', 'TOT_EMP']:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

            # Add a description column (can be replaced by ONET data later)
            df['Description'] = df['Occupation']

            return df[['Occupation', 'Description', 'A_MEAN', 'A_MEDIAN', 'H_MEAN', 'TOT_EMP']]

        except Exception as e:
            print("Error loading job dataset:", e)
            return pd.DataFrame(columns=['Occupation', 'Description', 'A_MEAN', 'A_MEDIAN', 'H_MEAN', 'TOT_EMP'])

    @functools.lru_cache(maxsize=1)
    def _read_geo_file(self):
        print("📊 Loading geographic dataset (cached)...")
        df = pd.read_excel(
            "project_data/oesm24all/all_data_M_2024.xlsx",
            usecols=["AREA", "AREA_TITLE", "OCC_TITLE", "TOT_EMP"]
        ).dropna()
        print(f"✅ Geographic dataset loaded: {len(df)} rows")
        return df

    def load_geographic_job_data(self, occupation_filter=None):
        try:
            df = self._read_geo_file()

            # ✅ Keep only rows that represent entire states or the U.S.
            df = df[~df["AREA_TITLE"].str.contains("metropolitan|nonmetropolitan", case=False, na=False)]

            # ✅ Include both U.S. and state totals
            df = df[df["AREA_TITLE"].isin([
                "U.S.", "United States"
            ]) | (df["AREA_TITLE"].isin([
>>>>>>> 25283421 (🚀 Rebuilt Monty project with new architecture and parser)
                "Alabama","Alaska","Arizona","Arkansas","California","Colorado","Connecticut","Delaware",
                "District of Columbia","Florida","Georgia","Hawaii","Idaho","Illinois","Indiana","Iowa",
                "Kansas","Kentucky","Louisiana","Maine","Maryland","Massachusetts","Michigan","Minnesota",
                "Mississippi","Missouri","Montana","Nebraska","Nevada","New Hampshire","New Jersey",
                "New Mexico","New York","North Carolina","North Dakota","Ohio","Oklahoma","Oregon",
                "Pennsylvania","Rhode Island","South Carolina","South Dakota","Tennessee","Texas","Utah",
                "Vermont","Virginia","Washington","West Virginia","Wisconsin","Wyoming"
<<<<<<< HEAD
            ]
            df = df[df["AREA_TITLE"].isin(state_list + ["U.S.", "United States"])]

            # Apply occupation filter early to save memory
            if occupation_filter:
                occ_pattern = occupation_filter.strip().lower()
                df = df[df["OCC_TITLE"].str.lower().str.contains(occ_pattern, na=False)]

            print(f"✅ Filtered geographic data: {len(df)} rows for '{occupation_filter or 'ALL'}'")
            return df.reset_index(drop=True)
        except Exception as e:
            print("❌ Error loading geographic job data:", e)
            return pd.DataFrame()
=======
            ]))]

            print(f"✅ Filtered to {len(df)} state/U.S. rows")

            return df

        except Exception as e:
            print("Error loading geographic job data:", e)
            return pd.DataFrame()



>>>>>>> 25283421 (🚀 Rebuilt Monty project with new architecture and parser)
