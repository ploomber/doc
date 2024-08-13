
from dash import html, dcc, Output, Input, Dash
import dash_bootstrap_components as dbc
from datetime import datetime
import requests

default_fig = dict(
    data=[{'x': [], 'y': [], 'name': 'BTC/USDT'}],
    layout=dict(
        title=dict(text='Live Bitcoin Price Tracker: 5-Minute Rolling Window (BTC/USDT)', font=dict(color='white')),
        xaxis=dict(autorange=True, tickformat="%H:%M:%S", nticks=8, color='white'),
        yaxis=dict(autorange=True, color="white"),
        paper_bgcolor="#2D2D2D",
        plot_bgcolor="#2D2D2D"
    ))

app = Dash(external_stylesheets=[dbc.themes.CYBORG])
app.layout = html.Div([
    html.H1("Live Bitcoin Price Tracker",
        style={"text-align":"center",
               "padding-top":"40px",
               "padding-bottom":"20px"}),
    html.Hr(), 
    html.H2(id="price-ticker",
        style={"text-align":"center",
               "padding-top":"20px",
               "padding-bottom":"20px"}),
    dcc.Graph(id="graph-price-change", figure=default_fig),
    dcc.Interval(id="update", interval=4000),
    ])

@app.callback(
        Output("graph-price-change", "extendData"),
        Output("price-ticker", "children"),
        Input("update", "n_intervals"),
        )
def update_data(intervals):
    time = datetime.now().strftime("%H:%M:%S")
    response = requests.get('https://api.binance.us/api/v3/ticker/price?symbol=BTCUSDT')
    if response.status_code != 200:
        return default_fig, f"Failed to fetch data: {response}"
    data = response.json()
    price = float(data['price'])
    return {
        'x': [[time]],
        'y': [[price]]
    }, f"Current BTC/USDT Price: {price:.2f}"


if __name__ == "__main__":
    app.run_server(debug=True)