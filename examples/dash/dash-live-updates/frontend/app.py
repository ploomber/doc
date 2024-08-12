
from dash import html, dcc, Output, Input, Dash, State
import dash_bootstrap_components as dbc
import os
import psycopg2
from datetime import datetime

update_frequency = 2000

default_fig = lambda title: dict(
    data=[{'x': [], 'y': [], 'name': title}],
    layout=dict(
        title=dict(text=title, font=dict(color='white')),
        xaxis=dict(autorange=True, tickformat="%H:%M:%S", color='white', nticks=8),
        yaxis=dict(autorange=True, color="white"),
        paper_bgcolor="#2D2D2D",
        plot_bgcolor="#2D2D2D"
    ))

app = Dash()
app.layout = html.Div([

    html.H1(id="price-ticker",
        style={"text-align":"center",
               "padding-top":"40px",
               "padding-bottom":"40px"}),
    dcc.Graph(id="graph-price-change", figure = default_fig("Bitcoin Price Change (Last 5 min)")),
    dcc.Graph(id="graph-agg-per-min", figure = default_fig("Bitcoin Aggregated Trades per Minute (Last 5 min)")),
    dcc.Interval(id="update", interval = update_frequency),
    ])

@app.callback(
        Output("graph-price-change", "extendData"),
        Output("graph-agg-per-min", "extendData"),
        Output("price-ticker", "children"),
        Input("update", "n_intervals"),
        )
def update_data(intervals):

    CONNECTION = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
    with psycopg2.connect(CONNECTION) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM trades WHERE time > NOW() - INTERVAL '1 min'")
        rows = cursor.fetchall()

    current_price = rows[-1][2]
    total_trades = len(rows)

    new_data_price_change = dict(x=[[datetime.now().strftime("%H:%M:%S")]], y=[[current_price]])
    new_data_agg_per_min = dict(x=[[datetime.now().strftime("%H:%M:%S")]], y=[[total_trades]])
    # (new data, trace to add data to, number of elements to keep)
    return (new_data_price_change, [0], 20), (new_data_agg_per_min, [0], 20),  f"Current BTC price: {current_price}"


if __name__ == "__main__":
    app.run_server(debug=True)