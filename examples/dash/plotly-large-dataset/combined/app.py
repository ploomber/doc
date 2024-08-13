from dash import dcc, html, Input, Output, Dash
import pandas as pd
from datetime import datetime as dt
import plotly.graph_objects as go
from plotly_resampler import FigureResampler

app = Dash(__name__)
server = app.server

N = 100000

df = pd.read_csv("data/flights-3m-cleaned.csv")

app.layout = html.Div(children=[
    html.H1("Plotting Large Datasets in Dash"),
    html.P("Select range of flight dates to visualize"),
    dcc.DatePickerRange(
        id="date-picker-select",
        start_date=dt(2006, 1, 1),
        end_date=dt(2006, 4, 1),
        min_date_allowed=dt(2006, 1, 1),
        max_date_allowed=dt(2006, 7, 1),
        initial_visible_month=dt(2006, 1, 1),
    ),
    dcc.Graph(id='example-graph'),

])

@app.callback(
    Output("example-graph", "figure"),
    [
        Input("date-picker-select", "start_date"),
        Input("date-picker-select", "end_date"),
    ],
)
def update_figure(start, end):
    start = start + " 00:00:00"
    end = end + " 00:00:00"

    df_filtered = df[(pd.to_datetime(df["DEP_DATETIME"]) >= pd.to_datetime(start)) & \
                     (pd.to_datetime(df["DEP_DATETIME"]) <= pd.to_datetime(end))]

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
        hf_x=df_filtered["DEP_DATETIME"],
        hf_y=df_filtered["DEP_DELAY"],
        max_n_samples=N
    )

    fig.update_layout(
        title="Flight departure delay",
        xaxis_title="Flight date and time (24h)",
        yaxis_title="Departure delay (minutes)"
    )

    return fig