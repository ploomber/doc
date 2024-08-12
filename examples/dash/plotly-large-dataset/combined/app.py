from dash import dcc, html, Dash
import pandas as pd
import plotly.graph_objects as go
from plotly_resampler import FigureResampler

app = Dash(__name__)
server = app.server

N = 100000

df = pd.read_csv("data/flights-3m-cleaned.csv")

fig = FigureResampler(go.Figure())

fig.add_trace(go.Scattergl(
        mode="markers", # Replace with "line-markers" if you want to display lines between time series data.
        showlegend=False, 
        line_width=0.3, 
        line_color="gray", 
        marker={
            "color": abs(df["DEP_DELAY"]), # Convert marker value to color.
            "colorscale": "Portland", # How marker color changes based on data point value.
            "size": abs(5 + df["DEP_DELAY"] / 50) # Non-negative size of individual data point marker based on the dataset.
        }
    ), 
    hf_x=df["DEP_DATETIME"],
    hf_y=df["DEP_DELAY"],
    max_n_samples=N
)

fig.update_layout(
    title="Flight departure delay",
    xaxis_title="Date and time",
    yaxis_title="Departure delay (minutes)"
)

app.layout = html.Div(children=[
    html.H1("Plotting Large Datasets in Dash"),
    dcc.Graph(id='example-graph', figure=fig),

])
