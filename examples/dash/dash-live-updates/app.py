from dash import html, dcc, Output, Input, Dash
import dash_bootstrap_components as dbc
import os, psycopg2

update_frequency = 4000
graph_title1 = "Price Change: 5-Minute Rolling Window (BTC/USDT)"
graph_title2 = "Aggregated Trades per Minute: 5-Minute Rolling Window"

default_fig = lambda title: dict(
    data=[{'x': [], 'y': [], 'name': title}],
    layout=dict(
        title=dict(text=title, font=dict(color='white')),
        xaxis=dict(autorange=True, tickformat="%H:%M:%S", color='white', nticks=8),
        yaxis=dict(autorange=True, color="white"),
        paper_bgcolor="#2D2D2D",
        plot_bgcolor="#2D2D2D"
    ))

# Initialize the Dash app
app = Dash(external_stylesheets=[dbc.themes.CYBORG])
server = app.server

app.layout = html.Div([
    html.H1("Live Bitcoin Monitoring App",
            style={"text-align":"center", "padding-top":"20px", "padding-bottom":"20px"}),
    html.Hr(), 
    html.H2(id="price-ticker",
            style={"text-align":"center", "padding-top":"10px", "padding-bottom":"10px"}),
    dcc.Graph(id="graph-price-change", figure=default_fig(graph_title1)),
    dcc.Graph(id="graph-agg-per-min", figure=default_fig(graph_title2)),
    dcc.Interval(id="update", interval=update_frequency),
    ])

previous_time = None
# Function to fetch data from the database
def fetch_data():
    global previous_time
    # Construct the connection string
    db_user = os.getenv('DB_USER')
    db_password = os.getenv('DB_PASSWORD')
    db_host = os.getenv('DB_HOST')
    db_port = os.getenv('DB_PORT')
    db_name = os.getenv('DB_NAME')

    if not all([db_user, db_password, db_host, db_port, db_name]):
        return None, "Database connection details are not fully set in environment variables"

    connection_string = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    try:
        with psycopg2.connect(connection_string) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT *
                FROM trades
                WHERE time >= (
                    SELECT MAX(time)
                    FROM trades
                ) - INTERVAL '1 minute';
            """)
            rows = cursor.fetchall()
            
            if not rows or (previous_time and rows[0][0] <= previous_time): 
                print("No data available - Are you running websocket_backend.py?")
                return None, "No data available"

            previous_time = rows[0][0]
            
            return rows, None
    
    except psycopg2.Error as e:
        print(f"Database connection error: {e}")
        return None, "Database connection error"

# Callback to extend the data in the graphs
@app.callback(
        Output("graph-price-change", "extendData"),
        Output("graph-agg-per-min", "extendData"),
        Output("price-ticker", "children"),
        Input("update", "n_intervals"),
        )
def update_data(intervals):
    rows, msg = fetch_data()
    if rows == None:
        return None, None, msg
    
    current_price = rows[0][1]
    total_trades = len(rows)
    new_data_price_change = dict(x=[[rows[0][0]]], y=[[current_price]])
    new_data_agg_per_min = dict(x=[[rows[0][0]]], y=[[total_trades]])
    print(f"Current X: {rows[0][0]}")

    # (new data, trace to add data to, number of elements to keep)
    return ((new_data_price_change, [0], 75),
            (new_data_agg_per_min, [0], 75),
            f"Current BTC price: {current_price}")

if __name__ == "__main__":
    app.run_server(debug=True)