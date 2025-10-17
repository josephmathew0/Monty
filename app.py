import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import base64
import os
import uuid
import re
import pandas as pd

from components.DataAndModelInitializer import DataAndModelInitializer
from components.EmbeddingProcessor import EmbeddingProcessor
from components.linkedin_pdf_parser import extract_linkedin_info
from components.VisualizationTools import VisualizationTools

# -------------------------------
# Setup
# -------------------------------
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = dash.Dash(__name__)
app.title = "Monty - LinkedIn Career Insight"

<<<<<<< HEAD
# Global placeholders (loaded lazily)
data_loader = None
matcher = None
job_df = None
viz_tools = None
_geo_cache = None


# -------------------------------
# Helper: Lazy initialization
# -------------------------------
def ensure_initialized():
    """Initialize heavy components only once."""
    global data_loader, matcher, job_df, viz_tools
    if data_loader is None:
        print("🧠 Initializing model and data on demand...")
        data_loader = DataAndModelInitializer()
        model = data_loader.load_model()
        job_df_local = data_loader.load_job_data()
        matcher_local = EmbeddingProcessor(model)
        viz_tools_local = VisualizationTools()
        # assign globals
        globals().update({
            "matcher": matcher_local,
            "job_df": job_df_local,
            "viz_tools": viz_tools_local,
        })


def get_geo_df(top_job_title=None):
    """Load geographic data only when absolutely required."""
    global _geo_cache
    if _geo_cache is not None:
        return _geo_cache
    try:
        if data_loader is None:
            ensure_initialized()
        _geo_cache = data_loader.load_geographic_job_data(top_job_title)
    except Exception as e:
        print("⚠️ Could not load geographic data:", e)
        _geo_cache = pd.DataFrame()
    return _geo_cache


# -------------------------------
# Helpers for parsing
# -------------------------------
def save_pdf(contents):
=======
# -------------------------------
# Load models and data
# -------------------------------
data_loader = DataAndModelInitializer()
model = data_loader.load_model()
job_df = data_loader.load_job_data()
matcher = EmbeddingProcessor(model)
viz_tools = VisualizationTools()

# -------------------------------
# Helper functions
# -------------------------------
def save_pdf(contents):
    """Temporarily save uploaded PDF."""
>>>>>>> 25283421 (🚀 Rebuilt Monty project with new architecture and parser)
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    file_path = os.path.join(UPLOAD_FOLDER, f"{uuid.uuid4()}.pdf")
    with open(file_path, 'wb') as f:
        f.write(decoded)
    return file_path


def clean_match_input(profile):
<<<<<<< HEAD
=======
    """Combine cleaned text fields for embedding matching."""
>>>>>>> 25283421 (🚀 Rebuilt Monty project with new architecture and parser)
    def clean(text):
        if not text:
            return ""
        text = re.sub(r"http\S+|www\S+|linkedin\S+", "", text)
        text = re.sub(r"\([^)]*\)", "", text)
        text = re.sub(r"Page \d+ of \d+", "", text)
        return text.strip()

    title = clean(profile['title'])
    summary = clean(profile['summary'])
    education = clean(profile['education'])
    skills = clean(profile['skills'])
    experience = clean(profile['experience'])
<<<<<<< HEAD
    return f"{title}. {summary}. {education}. {skills}. {experience}"


# -------------------------------
# Upload Preview
=======

    combined = f"{title}. {summary}. {education}. {skills}. {experience}"
    return combined


# -------------------------------
# Upload preview callback
>>>>>>> 25283421 (🚀 Rebuilt Monty project with new architecture and parser)
# -------------------------------
@app.callback(
    Output('upload-preview', 'children'),
    Input('upload-pdf', 'contents'),
    State('upload-pdf', 'filename'),
    State('upload-pdf', 'last_modified')
)
def update_upload_preview(contents, filename, last_modified):
<<<<<<< HEAD
    if contents:
=======
    if contents is not None:
>>>>>>> 25283421 (🚀 Rebuilt Monty project with new architecture and parser)
        try:
            _, content_string = contents.split(',')
            decoded = base64.b64decode(content_string)
            size_kb = round(len(decoded) / 1024, 1)
        except Exception:
            size_kb = "unknown"

        return html.Div([
            html.P(f"✅ Uploaded: {filename} ({size_kb} KB)", style={'color': 'green', 'fontWeight': 'bold'}),
            html.P("Now click Submit to analyze your profile.", style={'color': 'gray', 'fontStyle': 'italic'})
        ])
    return html.P("No file uploaded yet.", style={'color': 'gray'})


# -------------------------------
# Layout
# -------------------------------
app.layout = html.Div([
    html.H2("Welcome to Monty!"),
    html.P("📄 Upload your LinkedIn Profile PDF to analyze your career path."),

    dcc.Upload(
        id='upload-pdf',
        children=html.Div(['Drag & drop or ', html.A('select a PDF')]),
        style={
            'width': '100%', 'height': '80px', 'lineHeight': '80px',
            'borderWidth': '2px', 'borderStyle': 'dashed',
            'borderRadius': '5px', 'textAlign': 'center', 'margin': '10px 0'
        },
        multiple=False,
        accept='.pdf'
    ),

    html.Div(id='upload-preview'),
<<<<<<< HEAD
    html.Button('Submit', id='submit-button', n_clicks=0),

=======

    html.Button('Submit', id='submit-button', n_clicks=0),

    # -----------------------------
    # Region filter dropdown
    # -----------------------------
>>>>>>> 25283421 (🚀 Rebuilt Monty project with new architecture and parser)
    html.Div([
        html.Label("🌎 Filter by Region:"),
        dcc.Dropdown(
            id='region-filter',
            options=[
                {'label': 'All Regions', 'value': 'All'},
                {'label': 'West', 'value': 'West'},
                {'label': 'Midwest', 'value': 'Midwest'},
                {'label': 'South', 'value': 'South'},
                {'label': 'Northeast', 'value': 'Northeast'},
            ],
            value='All',
            clearable=False,
            style={'width': '300px'}
        )
    ], style={'marginTop': '20px', 'marginBottom': '10px'}),

<<<<<<< HEAD
=======
    # Output section (profile, charts, maps)
>>>>>>> 25283421 (🚀 Rebuilt Monty project with new architecture and parser)
    dcc.Loading(
        id='loading-section',
        type='circle',
        fullscreen=False,
        children=html.Div(id='output-section')
    )
])


# -------------------------------
<<<<<<< HEAD
# Main callback
=======
# Main callback for processing & visualization
>>>>>>> 25283421 (🚀 Rebuilt Monty project with new architecture and parser)
# -------------------------------
@app.callback(
    Output('output-section', 'children'),
    [Input('submit-button', 'n_clicks'),
     Input('region-filter', 'value')],
    [State('upload-pdf', 'contents')]
)
def update_output(n_clicks, region_filter, contents):
<<<<<<< HEAD
    if n_clicks > 0 and contents:
        ensure_initialized()  # Initialize model/data on demand

        pdf_path = save_pdf(contents)
        profile = extract_linkedin_info(pdf_path)
=======
    if n_clicks > 0 and contents is not None:
        pdf_path = save_pdf(contents)
        profile = extract_linkedin_info(pdf_path)

>>>>>>> 25283421 (🚀 Rebuilt Monty project with new architecture and parser)
        match_input = clean_match_input(profile)
        top_roles = matcher.find_top_roles(match_input, job_df)
        top_job_title = top_roles[0][0] if top_roles else None

<<<<<<< HEAD
        geo_df = get_geo_df(top_job_title) if top_job_title else pd.DataFrame()
        print(f"Geo DF rows: {len(geo_df)}")
=======
        geo_df = data_loader.load_geographic_job_data(top_job_title) if top_job_title else pd.DataFrame()
        print(f"Unique titles in geo_df: {geo_df['OCC_TITLE'].unique()[:20] if not geo_df.empty else 'None'}")
>>>>>>> 25283421 (🚀 Rebuilt Monty project with new architecture and parser)

        salary_chart, role_salary, national_salary = (
            viz_tools.generate_salary_chart(job_df, top_job_title)
            if top_job_title else (None, None, None)
        )

<<<<<<< HEAD
=======
        # Generate geographic map with region filter
>>>>>>> 25283421 (🚀 Rebuilt Monty project with new architecture and parser)
        geo_map_html = viz_tools.generate_geographic_map(
            geo_df, top_job_title, region_filter
        ) if not geo_df.empty else ""

        ratio = round(role_salary / national_salary, 1) if national_salary else None
        direction = "higher" if ratio and ratio >= 1 else "lower"
        comparison_text = f"{ratio}× {direction}" if ratio else "N/A"
        role_salary_fmt = f"${int(role_salary):,}" if role_salary else "N/A"
        national_salary_fmt = f"${int(national_salary):,}" if national_salary else "N/A"

<<<<<<< HEAD
=======
        print(f"Top job title: {top_job_title}")
        print(f"Geo DF rows: {len(geo_df)}")

>>>>>>> 25283421 (🚀 Rebuilt Monty project with new architecture and parser)
        interpretation_text = html.Div([
            html.P("💡 Insight:", style={'fontWeight': 'bold', 'marginBottom': '5px', 'fontSize': '16px'}),
            html.P(
                f"If you pursue a role like {top_job_title}, your expected average salary is "
                f"approximately {comparison_text} than the national average "
                f"({role_salary_fmt} vs {national_salary_fmt}).",
                style={'margin': '0', 'color': '#333'}
            )
        ], style={
            'backgroundColor': '#f9f9f9',
            'borderLeft': '5px solid #00b894',
            'padding': '12px',
            'marginTop': '15px',
            'borderRadius': '5px',
<<<<<<< HEAD
            'boxShadow': '1px 1px 4px rgba(0,0,0,0.05)'
=======
            'boxShadow': '1px 1px 4px rgba(0, 0, 0, 0.05)'
>>>>>>> 25283421 (🚀 Rebuilt Monty project with new architecture and parser)
        })

        return html.Div([
            html.H4("🔍 Extracted Profile Information:"),
            html.P(f"👤 Name: {profile['name']}"),
            html.P(f"💼 Title: {profile['title']}"),
            html.P(f"📍 Location: {profile['location']}"),
            html.P(f"🧾 Summary: {profile['summary']}"),
            html.P(f"🎓 Education: {profile['education']}"),
            html.P(f"🧠 Skills: {profile['skills']}"),
            html.P(f"📜 Experience: {profile['experience'][:300]}..."),

            html.H4("📈 Top 3 Suggested Job Roles:"),
            html.Ul([html.Li(f"{role} (score: {score:.4f})") for role, score in top_roles]),

            html.Hr(),
            html.H4("💰 Salary Comparison:"),
            salary_chart,
            interpretation_text,

            html.Hr(),
            html.H4("🗺 Geographic Distribution of Jobs:"),
            dcc.Markdown("This map shows which U.S. states employ the highest number of workers in your suggested job role."),
            html.Iframe(srcDoc=geo_map_html, width="100%", height="500")
        ])
<<<<<<< HEAD
=======

>>>>>>> 25283421 (🚀 Rebuilt Monty project with new architecture and parser)
    return ""


# -------------------------------
<<<<<<< HEAD
# Run server
# -------------------------------
if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 8050))
    app.run_server(host="0.0.0.0", port=port, debug=False)

=======
# Run the server
# -------------------------------
if __name__ == '__main__':
    app.run_server(debug=True)
>>>>>>> 25283421 (🚀 Rebuilt Monty project with new architecture and parser)
