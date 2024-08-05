"""
Taken from Dash's documentation: https://dash.plotly.com/minimal-app
"""
from dash import Dash, html, dcc, callback, Output, Input
import plotly.express as px
import pandas as pd
import ssl
from flask import g

ssl._create_default_https_context = ssl._create_unverified_context

def init_app(url_path, server=None):
    global df

    # Initialize Dash app with or without specifying flask server
    app =  Dash(server=server, url_base_pathname=url_path) if server else Dash(requests_pathname_prefix=url_path)

    # Use data from server context if server is available
    df = g.df if server else pd.read_csv(
        "https://raw.githubusercontent.com/plotly/datasets/master/gapminder_unfiltered.csv"
    )
    server = app.server

    app.title = "Population by country - Ploomber Cloud Dash Application"

    app.layout = html.Div(
        [
            html.A(id="logout-link", children="Main page", href="/"),
            html.H1(children="Population by country", style={"textAlign": "center"}),
            dcc.Dropdown(df.country.unique(), "Canada", id="dropdown-selection"),
            dcc.Graph(id="graph-content"),
        ]
    )

    init_callbacks(app)
    return server


def update_graph(value):
    dff = df[df.country == value]
    return px.line(dff, x="year", y="pop")

def init_callbacks(app):
    app.callback(
        Output("graph-content", "figure"), 
        Input("dropdown-selection", "value")
    )(update_graph)
