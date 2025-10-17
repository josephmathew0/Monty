import plotly.graph_objs as go
from dash import dcc
import pandas as pd
import json
import folium
from folium.plugins import MarkerCluster


class VisualizationTools:
    def generate_salary_chart(self, job_df, matched_role):
        try:
            matched_role = matched_role.strip().lower()

            # Get role salary
            role_row = job_df[job_df['Occupation'].str.lower() == matched_role]
            role_salary = role_row['A_MEAN'].values[0] if not role_row.empty else None

            # Get national average salary
            national_row = job_df[job_df['Occupation'].str.lower() == 'all occupations']
            national_salary = national_row['A_MEAN'].values[0] if not national_row.empty else None

            if role_salary is None or national_salary is None:
                return dcc.Markdown("⚠️ Salary data not available for this role."), None, None

            # Bar chart
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


    def generate_geographic_map(self, geo_df, job_title, region_filter="All"):
        """
        Generate a geographic map showing job distribution by U.S. state.
        Supports hover tooltips, click toggle popups, and regional filtering.
        """
        try:
            import branca.colormap as cm

            # Load coordinates
            with open("project_data/us_state_centroids.json") as f:
                state_coords = json.load(f)

            # Define U.S. regions (Census Bureau)
            region_map = {
                "West": [
                    "California", "Oregon", "Washington", "Nevada", "Idaho",
                    "Montana", "Wyoming", "Utah", "Colorado", "Alaska", "Hawaii"
                ],
                "Midwest": [
                    "North Dakota", "South Dakota", "Nebraska", "Kansas", "Minnesota",
                    "Iowa", "Missouri", "Wisconsin", "Illinois", "Indiana", "Michigan", "Ohio"
                ],
                "South": [
                    "Delaware", "Maryland", "Virginia", "West Virginia", "Kentucky",
                    "Tennessee", "North Carolina", "South Carolina", "Georgia",
                    "Florida", "Alabama", "Mississippi", "Arkansas", "Louisiana", "Texas", "Oklahoma"
                ],
                "Northeast": [
                    "Maine", "New Hampshire", "Vermont", "Massachusetts", "Rhode Island",
                    "Connecticut", "New York", "New Jersey", "Pennsylvania"
                ]
            }

            df = geo_df.copy()
            df["OCC_TITLE"] = df["OCC_TITLE"].astype(str).str.lower().str.strip()
            df["AREA_TITLE"] = df["AREA_TITLE"].astype(str).str.strip()
            df["TOT_EMP"] = pd.to_numeric(df["TOT_EMP"], errors="coerce").fillna(0)

            job_lower = job_title.lower().strip()

            filtered = df[df["OCC_TITLE"] == job_lower]
            if filtered.empty:
                filtered = df[df["OCC_TITLE"].str.contains(job_lower.split()[0], case=False, na=False)]

            print(f"[MAP DEBUG] {job_title} -> {len(filtered)} rows matched after robust filter")
            if filtered.empty:
                return "<div style='color:gray'>No geographic data available for this role.</div>"

            # Aggregate by state
            state_data = (
                filtered.groupby("AREA_TITLE", as_index=False)["TOT_EMP"]
                .sum()
                .sort_values(by="TOT_EMP", ascending=False)
            )
            state_data["TOT_EMP"] = pd.to_numeric(state_data["TOT_EMP"], errors="coerce").fillna(0)

            # Apply regional filter if requested
            if region_filter != "All":
                allowed_states = region_map.get(region_filter, [])
                state_data = state_data[state_data["AREA_TITLE"].isin(allowed_states)]
                print(f"[MAP DEBUG] Applied region filter: {region_filter} ({len(state_data)} states)")

            if state_data.empty:
                return f"<div style='color:gray'>No data available for {region_filter} region.</div>"

            # Color scale
            min_jobs, max_jobs = state_data["TOT_EMP"].min(), state_data["TOT_EMP"].max()
            colormap = cm.LinearColormap(
                colors=["#FFEDA0", "#FEB24C", "#F03B20", "#800026"],
                vmin=min_jobs,
                vmax=max_jobs,
            )
            colormap.caption = "Number of Jobs by State"

            # Initialize map
            m = folium.Map(location=[39.8283, -98.5795], zoom_start=4, tiles="CartoDB positron")

            # Add circles with hover + click toggle
            for _, row in state_data.iterrows():
                state_name = row["AREA_TITLE"].strip().replace("U.S.", "United States")
                jobs = int(row["TOT_EMP"])
                if jobs <= 0 or state_name not in state_coords:
                    continue
                lat, lon = state_coords[state_name]
                color = colormap(jobs)

                # Popup and hover tooltip
                popup_html = f"<b>{state_name}</b><br>{jobs:,} jobs"
                tooltip_html = f"{state_name}: {jobs:,} jobs"

                folium.CircleMarker(
                    location=[lat, lon],
                    radius=6 + (jobs ** 0.5) / 12,
                    color=color,
                    fill=True,
                    fill_color=color,
                    fill_opacity=0.75,
                    popup=folium.Popup(popup_html, show=False),
                    tooltip=tooltip_html,
                ).add_to(m)

            # Title
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

