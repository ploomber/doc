import panel as pn
import hvplot.pandas
import pandas as pd
import duckdb

# Initialize Panel with extensions for plotting
pn.extension('hvplot')

# Define the stock symbols you're interested in for the dropdown
stock_symbols = ["AAPL", "GOOGL", "MSFT", "AMZN", "FB"]

# UI Components for stock selection
ticker_input = pn.widgets.Select(name='Stock Symbol', options=stock_symbols, value='AAPL')
start_date = pn.widgets.DatePicker(name='Start Date', value=pd.to_datetime('2022-01-01'))
end_date = pn.widgets.DatePicker(name='End Date', value=pd.to_datetime('2024-01-01'))

# Visualization area where the plot will be displayed
visualization_area = pn.pane.HoloViews()

# Database file path
db_file = "stockdata.duckdb"

def get_stock_data_from_duckdb(ticker, start_date, end_date):
    """
    Fetches stock data for a given ticker from a DuckDB database.
    """
    query = f"""
    SELECT Date, Close
    FROM {ticker.lower()}
    WHERE Date BETWEEN '{start_date.strftime('%Y-%m-%d')}' AND '{end_date.strftime('%Y-%m-%d')}'
    """
    conn = duckdb.connect(db_file)
    data = conn.execute(query).fetchdf()
    conn.close()
    return data

def update_visualization(ticker, start, end):
    # Fetch the stock data from DuckDB
    data = get_stock_data_from_duckdb(ticker, start, end)
    # Generate the plot
    plot = data.hvplot.line('Date', 'Close', width=800, height=400, title=f'{ticker} Closing Price')
    # Update the visualization area with the new plot
    visualization_area.object = plot

# Example callback function to trigger plot update on selection change
def on_selection_change(event):
    update_visualization(ticker_input.value, start_date.value, end_date.value)

# Watch for changes in the UI components
ticker_input.param.watch(on_selection_change, 'value')
start_date.param.watch(on_selection_change, 'value')
end_date.param.watch(on_selection_change, 'value')

# Trigger initial plot update
update_visualization(ticker_input.value, start_date.value, end_date.value)

# Organize the layout
input_column = pn.Column("# Input Parameters", ticker_input, start_date, end_date)
visualization_column = pn.Column("# Visualization", visualization_area)

# Main layout
main_layout = pn.Row(input_column, visualization_column)

# Serve the Panel app
main_layout.servable()
