import plotly.graph_objs as go
from dash import dcc
import pandas as pd
import json
import folium
import branca.colormap as cm
import re


class VisualizationTools:
    # ------------------------------
    # Salary Comparison Chart
    # ------------------------------
    def generate_salary_chart(self, job_df, matched_role):
        try:
            matched_role = matched_role.strip().lower()

            # Get role salary
            role_row = job_df[job_df['Occupation'].str.lower() == matched_role]
            role_salary = role_row['A_MEAN'].values[0] if not role_row.empty else None

            # Get national average
            national_row = job_df[job_df['Occupation'].str.lower() == 'all occupations']
            national_salary = national_row['A_MEAN'].values[0] if not national_row.empty else None

            if role_salary is None or national_salary is None:
                return dcc.Markdown("⚠️ Salary data not available for this role."), None, None

            # Plot comparison chart
            fig = go.Figure(data=[
                go.Bar(name=matched_role.title(), x=['Salary'], y=[role_salary], marker_color='royalblue'),
                go.Bar(name='National Average', x=['Salary'], y=[national_salary], marker_color='tomato')
            ])
            fig.update_layout(
                title=f"💰 Salary Comparison (Annual Mean)",
                yaxis_title='USD ($)',
                barmode='group',
                height=400
            )
            return dcc.Graph(figure=fig), role_salary, national_salary

        except Exception as e:
            return dcc.Markdown(f"❌ Error generating salary chart: {e}"), None, None


    # ------------------------------
    # Geographic Job Distribution Map
    # ------------------------------
    def generate_geographic_map(self, geo_df, job_title, region_filter="All"):
        """Generate a Folium map showing employment distribution across U.S. states."""
        try:
            # Load state coordinates
            with open("project_data/us_state_centroids.json") as f:
                state_coords = json.load(f)

            # Define Census Bureau regions
            region_map = {
                "West": ["California","Oregon","Washington","Nevada","Idaho","Montana","Wyoming",
                         "Utah","Colorado","Alaska","Hawaii"],
                "Midwest": ["North Dakota","South Dakota","Nebraska","Kansas","Minnesota","Iowa",
                            "Missouri","Wisconsin","Illinois","Indiana","Michigan","Ohio"],
                "South": ["Delaware","Maryland","Virginia","West Virginia","Kentucky","Tennessee",
                          "North Carolina","South Carolina","Georgia","Florida","Alabama","Mississippi",
                          "Arkansas","Louisiana","Texas","Oklahoma"],
                "Northeast": ["Maine","New Hampshire","Vermont","Massachusetts","Rhode Island",
                              "Connecticut","New York","New Jersey","Pennsylvania"]
            }

            df = geo_df.copy()
            df["OCC_TITLE"] = df["OCC_TITLE"].astype(str).str.strip()
            df["AREA_TITLE"] = df["AREA_TITLE"].astype(str).str.strip()
            df["TOT_EMP"] = pd.to_numeric(df["TOT_EMP"], errors="coerce").fillna(0)

            # --------------------
            # Extract U.S. state from AREA_TITLE
            # --------------------
            state_list = [
                "Alabama","Alaska","Arizona","Arkansas","California","Colorado","Connecticut",
                "Delaware","District of Columbia","Florida","Georgia","Hawaii","Idaho","Illinois",
                "Indiana","Iowa","Kansas","Kentucky","Louisiana","Maine","Maryland","Massachusetts",
                "Michigan","Minnesota","Mississippi","Missouri","Montana","Nebraska","Nevada",
                "New Hampshire","New Jersey","New Mexico","New York","North Carolina","North Dakota",
                "Ohio","Oklahoma","Oregon","Pennsylvania","Rhode Island","South Carolina",
                "South Dakota","Tennessee","Texas","Utah","Vermont","Virginia","Washington",
                "West Virginia","Wisconsin","Wyoming"
            ]

            def extract_state(area_title):
                for state in state_list:
                    if state.lower() in area_title.lower():
                        return state
                return None

            df["STATE"] = df["AREA_TITLE"].apply(extract_state)
            df = df.dropna(subset=["STATE"])

            # --------------------
            # Normalize occupation titles
            # --------------------
            def normalize_text(text):
                text = re.sub(r'[^a-z0-9]+', ' ', str(text).lower())
                return re.sub(r'\s+', ' ', text).strip()

            df["OCC_CLEAN"] = df["OCC_TITLE"].apply(normalize_text)
            job_clean = normalize_text(job_title)

            # --------------------
            # Flexible occupation matching
            # --------------------
            filtered = df[df["OCC_CLEAN"].str.contains(job_clean, na=False)]

            # Broader fallback if exact phrase not found
            if filtered.empty:
                job_words = set(job_clean.split())
                filtered = df[df["OCC_CLEAN"].apply(lambda t: len(set(t.split()) & job_words) >= 2)]
                print(f"[MAP DEBUG] Applied 2-word overlap fallback: {len(filtered)} rows")

            # If still no match, try regex of individual words
            if filtered.empty and len(job_clean.split()) > 0:
                pattern = "|".join(job_clean.split())
                filtered = df[df["OCC_CLEAN"].str.contains(pattern, na=False)]
                print(f"[MAP DEBUG] Applied regex fallback: {len(filtered)} rows")

            print(f"[MAP DEBUG] {job_title} -> {len(filtered)} rows matched after normalized fuzzy search")

            if filtered.empty:
                return "<div style='color:gray'>No geographic data available for this role.</div>"

            # --------------------
            # Aggregate by state
            # --------------------
            state_data = (
                filtered.groupby("STATE", as_index=False)["TOT_EMP"]
                .sum()
                .sort_values(by="TOT_EMP", ascending=False)
            )

            # Apply region filter
            if region_filter != "All":
                allowed = region_map.get(region_filter, [])
                state_data = state_data[state_data["STATE"].isin(allowed)]
                print(f"[MAP DEBUG] Applied region filter: {region_filter} ({len(state_data)} states)")

            if state_data.empty:
                return f"<div style='color:gray'>No data available for {region_filter} region.</div>"

            # --------------------
            # Create Folium map
            # --------------------
            min_jobs, max_jobs = state_data["TOT_EMP"].min(), state_data["TOT_EMP"].max()
            colormap = cm.LinearColormap(
                colors=["#E0F3DB", "#A8DDB5", "#43A2CA", "#0868AC"],
                vmin=min_jobs,
                vmax=max_jobs,
            )
            colormap.caption = "Employment Density"

            m = folium.Map(location=[39.5, -98.35], zoom_start=4, tiles="CartoDB positron")

            for _, row in state_data.iterrows():
                state = row["STATE"]
                jobs = int(row["TOT_EMP"])
                if state not in state_coords or jobs <= 0:
                    continue

                lat, lon = state_coords[state]
                color = colormap(jobs)
                popup = f"<b>{state}</b><br>{jobs:,} employed"

                folium.CircleMarker(
                    location=[lat, lon],
                    radius=max(4, (jobs ** 0.5) / 8),
                    color=color,
                    fill=True,
                    fill_color=color,
                    fill_opacity=0.85,
                    popup=folium.Popup(popup, show=False),
                    tooltip=f"{state}: {jobs:,} jobs",
                ).add_to(m)

            # Add title and legend
            title_html = f"""
            <div style="position: fixed; 
                        top: 10px; left: 50%; transform: translateX(-50%);
                        z-index: 9999; background-color: white; 
                        padding: 5px 15px; border-radius: 8px; 
                        font-weight: bold; box-shadow: 0px 0px 5px #999;">
                {job_title} Employment by State ({region_filter})
            </div>
            """
            m.get_root().html.add_child(folium.Element(title_html))
            colormap.add_to(m)

            print(f"[MAP DEBUG] ✅ Map generated for {region_filter} with {len(state_data)} states (hover+click enabled)")
            return m._repr_html_()

        except Exception as e:
            print("Error generating map:", e)
            return "<div style='color:red'>Map could not be generated.</div>"
