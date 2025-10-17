import pandas as pd
import functools
from sentence_transformers import SentenceTransformer


class DataAndModelInitializer:
    def __init__(self):
        self.model = None
        self.job_df = None
        self.geo_df = None

    # ---------------------------
    # Model loader
    # ---------------------------
    def load_model(self):
        """Load SentenceTransformer model only once."""
        if self.model is None:
            print("Loading SentenceTransformer model on demand...")
            # Lightweight embedding model suitable for Render’s free tier
            self.model = SentenceTransformer('paraphrase-MiniLM-L3-v2')
        return self.model

    # ---------------------------
    # Job-level dataset (national)
    # ---------------------------
    def load_job_data(self):
        """Load and preprocess national-level occupational dataset."""
        try:
            df = pd.read_excel('project_data/oesm23nat/national_M2023_dl.xlsx')
            keep_cols = ['OCC_TITLE', 'A_MEAN', 'A_MEDIAN', 'H_MEAN', 'TOT_EMP']
            df = (
                df[keep_cols]
                .dropna(subset=['OCC_TITLE'])
                .drop_duplicates(subset=['OCC_TITLE'])
                .rename(columns={'OCC_TITLE': 'Occupation'})
            )

            # Convert to numeric
            for col in ['A_MEAN', 'A_MEDIAN', 'H_MEAN', 'TOT_EMP']:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

            df['Description'] = df['Occupation']
            print(f"✅ Job dataset loaded: {len(df)} occupations")
            return df[['Occupation', 'Description', 'A_MEAN', 'A_MEDIAN', 'H_MEAN', 'TOT_EMP']]

        except Exception as e:
            print("❌ Error loading job dataset:", e)
            return pd.DataFrame(
                columns=['Occupation', 'Description', 'A_MEAN', 'A_MEDIAN', 'H_MEAN', 'TOT_EMP']
            )

    # ---------------------------
    # Geographic dataset (state-level)
    # ---------------------------
    @functools.lru_cache(maxsize=1)
    def _read_geo_file(self):
        """Load geographic employment dataset efficiently (cached)."""
        try:
            print("Loading lightweight geographic dataset (cached)...")

            # Load a limited subset to stay within Render’s 512 MB memory cap
            df = pd.read_excel(
                "project_data/oesm24all/all_data_M_2024.xlsx",
                usecols=["AREA_TITLE", "OCC_TITLE", "TOT_EMP", "H_MEAN"],
                nrows=100000,  # limit rows for free-tier performance
                engine="openpyxl",
                dtype={
                    "AREA_TITLE": "string",
                    "OCC_TITLE": "string",
                    "TOT_EMP": "float32",
                    "H_MEAN": "float32",
                },
            ).dropna(subset=["OCC_TITLE", "AREA_TITLE"])

            print(f"✅ Geographic base dataset loaded: {len(df)} rows")
            return df

        except Exception as e:
            print("❌ Error reading geographic dataset:", e)
            return pd.DataFrame(columns=["AREA_TITLE", "OCC_TITLE", "TOT_EMP", "H_MEAN"])

    def load_geographic_job_data(self, occupation_filter=None):
        """Return filtered geographic data for a given occupation (if provided)."""
        try:
            df = self._read_geo_file()

            # U.S. state list
            state_list = [
                "Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado",
                "Connecticut", "Delaware", "District of Columbia", "Florida", "Georgia",
                "Hawaii", "Idaho", "Illinois", "Indiana", "Iowa", "Kansas", "Kentucky",
                "Louisiana", "Maine", "Maryland", "Massachusetts", "Michigan", "Minnesota",
                "Mississippi", "Missouri", "Montana", "Nebraska", "Nevada", "New Hampshire",
                "New Jersey", "New Mexico", "New York", "North Carolina", "North Dakota",
                "Ohio", "Oklahoma", "Oregon", "Pennsylvania", "Rhode Island",
                "South Carolina", "South Dakota", "Tennessee", "Texas", "Utah",
                "Vermont", "Virginia", "Washington", "West Virginia", "Wisconsin", "Wyoming"
            ]

            df = df[df["AREA_TITLE"].isin(state_list + ["U.S.", "United States"])]

            # Apply occupation filter early to save memory
            if occupation_filter:
                occ_pattern = occupation_filter.strip().lower()
                df = df[df["OCC_TITLE"].str.lower().str.contains(occ_pattern, na=False)]

            print(f"✅ Filtered geographic data: {len(df)} rows for '{occupation_filter or 'ALL'}'")
            return df.reset_index(drop=True)

        except Exception as e:
            print("❌ Error filtering geographic job data:", e)
            return pd.DataFrame(columns=["AREA_TITLE", "OCC_TITLE", "TOT_EMP", "H_MEAN"])
