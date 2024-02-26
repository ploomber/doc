import panel as pn
import pandas as pd
import duckdb
import hvplot.pandas
import datetime
from chat import get_data_from_duckdb_with_natural_language_query, \
                sql_query_generator
from dotenv import load_dotenv
load_dotenv(".env")

# Initialize Panel with extensions for plotting
pn.extension('hvplot')


def update_visualization(ticker, start, end, instruction):
    # Fetch the stock data from DuckDB
    data = get_data_from_duckdb_with_natural_language_query(instruction, 
                                                            ticker, 
                                                            start, 
                                                            end)
    # Generate the plot
    plot = data.hvplot.line('Date', 'Close', 
                            width=800, height=400, 
                            title=f'{ticker} Closing Price')
    visualization_area.object = plot


# Example callback function to trigger plot update on selection change
def submit_action(event):
    update_visualization(ticker_input.value, 
                         start_date.value, 
                         end_date.value, 
                         instruction_input.value)

def reset_action(event):
    visualization_area.object = None



# Define the stock symbols you're interested in for the dropdown
stock_symbols = ["AAPL", "GOOGL", "MSFT", "AMZN", "FB"]

# UI Components for stock selection
ticker_input = pn.widgets.Select(name='Stock Symbol', 
                                 options=stock_symbols, 
                                 value='AAPL')
start_date = pn.widgets.DatePicker(name='Start Date', 
                                   value=pd.to_datetime('2022-01-01'))
end_date = pn.widgets.DatePicker(name='End Date', 
                                 value=pd.to_datetime('2024-01-01'))
instruction_input = pn.widgets.TextAreaInput(name='Instructions', 
                                             height=200)

# Visualization area where the plot will be displayed
visualization_area = pn.pane.HoloViews()
submit_button = pn.widgets.Button(name='Submit', button_type='primary')
reset_button = pn.widgets.Button(name='Reset', button_type='danger')

# Database file path
db_file = "stockdata.duckdb"
submit_button.on_click(submit_action)
reset_button.on_click(reset_action)

# Layout
input_column = pn.Column("# Input Parameters", 
                         ticker_input, 
                         start_date, 
                         end_date, 
                         instruction_input, 
                         submit_button, 
                         reset_button,
                         )
visualization_column = pn.Column("# Visualization", visualization_area)
main_layout = pn.Row(input_column, visualization_column)

main_layout.servable()
