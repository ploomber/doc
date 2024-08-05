from dash import dcc, html, Input, Output, Dash
from flask import request
def init_app(url_path, server=None):

    # Initialize Dash app with or without specifying flask server
    app =  Dash(server=server, url_base_pathname=url_path) if server else Dash(requests_pathname_prefix=url_path)

    app.layout = html.Div(children=[
        html.A(id="logout-link", children="Main page", href="/"),
        html.H1("Welcome to my Dash App", style={"textAlign": "center"}),
        html.Div(id="dummy"),
        dcc.Graph(
            id='example-graph',
            figure={
                'data': [
                    {'x': [1, 2, 3], 'y': [4, 1, 2], 'type': 'bar', 'name': 'Category 1'},
                    {'x': [1, 2, 3], 'y': [2, 4, 5], 'type': 'bar', 'name': 'Category 2'},
                ],
                'layout': {
                    'title': 'Dash Data Visualization'
                }
            }
        ),

    ])

    return app.server
