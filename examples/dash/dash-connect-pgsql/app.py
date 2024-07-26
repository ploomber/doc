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

DB_LIST = ['math', 'portuguese']

app = Dash(__name__)
server = app.server

app.title = "Student Data - Ploomber Cloud Dash Application with PostgreSQL"

app.layout = html.Div(
    [
        html.H1(children="Dash Application with PostgreSQL Demo", style={"textAlign": "center"}),
        html.Div(
            [
                html.Div([
                    html.P(children="Database selection:"),
                    dcc.Dropdown(
                        DB_LIST, "math", id="db-selection", 
                        className="drop-list"
                    )
                ], className="drop-wrapper"),
                html.Div([
                    html.P(children="Select x, y axis and facet for scatter plot:"),
                    dcc.Dropdown(id="scatter-selection-x", className="drop-list"),
                    dcc.Dropdown(id="scatter-selection-y", className="drop-list"),
                    dcc.Dropdown(id="scatter-selection-facet", className="drop-list")
                ], className="drop-wrapper"),
                html.Div([
                    html.P(children="Select x axis for bar chart:"),
                    dcc.Dropdown(id="bar-selection-x", className="drop-list")
                ], className="drop-wrapper")
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
        Output("scatter-selection-facet", "options"),
        Output("bar-selection-x", "options"),
        Output("scatter-selection-x", "value"),
        Output("scatter-selection-y", "value"),
        Output("scatter-selection-facet", "value"),
        Output("bar-selection-x", "value"),
    ], 
    Input("db-selection", "value")
)
def update_dropdown(value):
    """Updates dropdown list based on selected db."""
    e = create_engine(connection_string)
    query = f"SELECT * FROM {value}"
    with e.connect() as conn:
        df = pd.read_sql(query, conn)
        conn.close()
    e.dispose()
    cols = list(df.columns)
    return cols[4:9], cols[9:], cols[1:4], cols[1:], cols[4], cols[9], cols[1], cols[1]

@callback(
    Output("graph-content", "figure"), 
    [
        Input("db-selection", "value"),
        Input("scatter-selection-x", "value"),
        Input("scatter-selection-y", "value"),
        Input("scatter-selection-facet", "value"),
    ]
)
def update_graph(db_name, val_x, val_y, val_facet):
    """Updates scatter plot based on selected x and y axis."""
    e = create_engine(connection_string)
    query = f"SELECT * FROM {db_name}"
    with e.connect() as conn:
        df = pd.read_sql(query, conn)
        conn.close()
    e.dispose()
    title = f"Distribution of student {val_y} based on {val_x}, separated by student {val_facet}"
    return px.scatter(df, x=val_x, y=val_y, facet_col=val_facet, title=title)

@callback(
    Output("graph-bar", "figure"), 
    [
        Input("db-selection", "value"),
        Input("bar-selection-x", "value"),
    ]
)
def update_bar(db_name, val_x):
    e = create_engine(connection_string)
    query = f"SELECT {val_x}, COUNT({val_x}) FROM {db_name} GROUP BY {val_x}"
    with e.connect() as conn:
        df = pd.read_sql(query, conn)
        conn.close()
    e.dispose()
    title =f"Number of students based on {val_x}"
    return px.bar(df, x=val_x, y="count", title=title)

if __name__ == '__main__':
   app.run_server(debug=False, port=8000)
