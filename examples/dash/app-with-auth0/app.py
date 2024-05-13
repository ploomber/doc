from dash import dcc, html, Input, Output, Dash
from flask import request

app = Dash(__name__)
server = app.server

app.layout = html.Div(children=[
    html.Div(id="greeting"),
    html.Div(id="logout-link", children=[
        dcc.Markdown(id="logout-msg"),
        dcc.Link("Logout", href="/logout")
    ]),
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


@app.callback(Output("greeting", "children"), Input("dummy", "children"))
def display_user(_):
    user = request.headers.get('X-Auth-Name', 'Anonymous')
    return f"Welcome {user}!"

