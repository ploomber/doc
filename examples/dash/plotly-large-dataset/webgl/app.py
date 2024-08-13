from dash import dcc, html, Input, Output, Dash
from flask import request
import pandas as pd
import plotly.graph_objects as go

app = Dash(__name__)
server = app.server

N = 100000 # Limit number of rows to plot.

fig = go.Figure() # Initiate the figure.

df = pd.read_csv("data/flights-3m-cleaned.csv")

fig.add_trace(go.Scattergl(
    x=df["DEP_DATETIME"][:N],
    y=df["DEP_DELAY"][:N],
    mode="markers", # Replace with "line-markers" if you want to display lines between time series data.
    showlegend=False, 
    line_width=0.3, 
    line_color="gray", 
    marker={
            "color": abs(df["DEP_DELAY"][:N]), # Convert marker value to color.
            "colorscale": "Portland", # How marker color changes based on data point value.
            "size": abs(5 + df["DEP_DELAY"][:N] / 50) # Non-negative size of individual data point marker based on the dataset.
        }
    )
)

fig.update_layout(
    title="Flight departure delay",
    xaxis_title="Flight date and time (24h)",
    yaxis_title="Departure delay (minutes)"
)

app.layout = html.Div(children=[
    html.H1("Plotting Large Datasets in Dash"),
    html.H2("""Downsampled figure: Departure delay time of around 3 
million flights in the first half (1/1-6/30) of 2006"""),
    html.Div("""Click on the graph and drag 
your cursor around to zoom into any part of the graph you want."""
            , style={"margin-top": "10px"}),
    html.Div("""To revert the figure to its original state, click on the 
'Reset axes' button at the upper right corner of the figure."""
            , style={"margin-top": "10px"}),
    dcc.Graph(id='example-graph', figure=fig),
])
