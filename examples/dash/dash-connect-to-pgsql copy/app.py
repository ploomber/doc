from dash import Dash, html, dcc, callback, Output, Input
import plotly.express as px
import pandas as pd
from sqlalchemy import URL, create_engine
import os

# Connect to PostgreSQL database
connection_string = URL.create(
  'postgresql',
  username=os.getenv("PGUSER"),
  password=os.getenv("PGPASSWORD"),
  host=os.getenv("PGHOST"),
  database=os.getenv("PGDATABASE")
)

# Connect to PG and start a session
engine = create_engine(connection_string, pool_size=10, max_overflow=20)

DB_LIST = ['math', 'portuguese']

app = Dash(__name__)
server = app.server

app.title = "Student Data - Ploomber Cloud Dash Application with PostgreSQL"

app.layout = html.Div(
    [
        html.H1(children="Dash Application with PostgreSQL Demo", style={"textAlign": "center"}),
        html.Div(
            [
                html.P(children="database selection"),
                dcc.Dropdown(DB_LIST, "math", id="db-selection"),
                html.P(children="Select x axis for scatter plot"),
                dcc.Dropdown(id="scatter-selection-x"),
                html.P(children="Select y axis for scatter plot"),
                dcc.Dropdown(id="scatter-selection-y"),
                html.P(children="Select x axis for bar chart"),
                dcc.Dropdown(id="bar-selection-x"),
            ]
        ),
        dcc.Graph(id="graph-content"),
        dcc.Graph(id="graph-bar")
    ]
)

@callback(
    [
        Output("scatter-selection-x", "options"), 
        Output("scatter-selection-y", "options"),
        Output("bar-selection-x", "options"),
        Output("scatter-selection-x", "value"),
        Output("scatter-selection-y", "value"),
        Output("bar-selection-x", "value"),
    ], 
    Input("db-selection", "value")
)
def update_dropdown(value):
    """Updates dropdown list based on selected db."""
    query = f"SELECT * FROM {value}"
    with engine.connect() as conn:
        df = pd.read_sql(query, conn)
    cols = list(df.columns)
    return cols, cols, cols, cols[0], cols[1], cols[0]

@callback(
    Output("graph-content", "figure"), 
    [
        Input("db-selection", "value"),
        Input("scatter-selection-x", "value"),
        Input("scatter-selection-y", "value"),
    ]
)
def update_graph(db_name, val_x, val_y):
    """Updates scatter plot based on selected x and y axis."""
    query = f"SELECT * FROM {db_name}"
    with engine.connect() as conn:
        df = pd.read_sql(query, conn)
    title = f"{val_x} vs {val_y}"
    return px.scatter(df, x=val_x, y=val_y, title=title)

@callback(
    Output("graph-bar", "figure"), 
    [
        Input("db-selection", "value"),
        Input("bar-selection-x", "value"),
    ]
)
def update_bar(db_name, val_x):
    query = f"SELECT {val_x}, COUNT({val_x}) FROM {db_name} GROUP BY {val_x}"
    with engine.connect() as conn:
        df = pd.read_sql(query, conn)
    title =f"Distribution of {val_x}"
    return px.bar(df, x=val_x, y="count", title=title)

if __name__ == '__main__':
   app.run_server(debug=False)
