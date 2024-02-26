import panel as pn
import pandas as pd
import duckdb
import hvplot.pandas
import datetime
from chat import get_data_from_duckdb_with_natural_language_query, \
                natural_language_to_plot_assistant
from dotenv import load_dotenv
load_dotenv(".env")

# Initialize Panel with extensions for plotting
pn.extension('hvplot')


def update_visualization(ticker, start, end, data_instruction):
    # Fetch the stock data from DuckDB
    data = get_data_from_duckdb_with_natural_language_query(data_instruction, 
                                                            ticker, 
                                                            start, 
                                                            end)
    print(data.head())
    print(type(data))
    # Generate the plot
    plot = data.hvplot.line('Date', 'Close', 
                            width=800, height=400, 
                            title=f'{ticker} Closing Price',
                            by='Ticker'
                            )
    
    plot_dictionary = natural_language_to_plot_assistant(data_instruction, ticker, data)
    print(plot_dictionary)
    visualization_area.object = plot

def line_plot(data, column_a, column_b, title):
    """
    This function generates a line plot using hvplot.
    """
    if "Ticker" in data.columns:
        plot = data.hvplot.line(column_a, column_b, 
                                width=800, height=400, 
                                title=title,
                                by='Ticker'
                                )
    else:
        plot = data.hvplot.line(column_a, column_b, 
                                width=800, height=400, 
                                title=title,
                                )
    visualization_area.object = plot

def bar_plot(data, column_a, column_b, title):
    """
    This function generates a bar plot using hvplot.
    """
    if "Ticker" in data.columns:
        plot = data.hvplot.bar(column_a, column_b, 
                                width=800, height=400, 
                                title=title,
                                by='Ticker'
                                )
    else:
        plot = data.hvplot.bar(column_a, column_b, 
                                width=800, height=400, 
                                title=title,
                                )
    visualization_area.object = plot

# Example callback function to trigger plot update on selection change
def submit_action(event):
    update_visualization(ticker_input.value, 
                         start_date.value, 
                         end_date.value, 
                         instruction_input.value,
                         )

def reset_action(event):
    visualization_area.object = None



# Define the stock symbols you're interested in for the dropdown
stock_symbols = ["AAPL", "GOOGL", "MSFT", "AMZN", "FB"]

# UI Components for stock selection
ticker_input = pn.widgets.MultiSelect(name='Stock Symbol', 
                                 value=stock_symbols[0:2], 
                                    options=stock_symbols,
                                 )
start_date = pn.widgets.DatePicker(name='Start Date', 
                                   value=pd.to_datetime('2022-01-01'))
end_date = pn.widgets.DatePicker(name='End Date', 
                                 value=pd.to_datetime('2024-01-01'))
instruction_input = pn.widgets.TextAreaInput(name='What data would you like to see?', 
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
