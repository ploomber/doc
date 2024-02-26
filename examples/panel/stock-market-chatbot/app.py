import panel as pn
import pandas as pd
import duckdb
from bokeh.io import export_png
import hvplot.pandas
import datetime
from chat import get_data_from_duckdb_with_natural_language_query, analyze_image_with_text
from dotenv import load_dotenv
import base64
import holoviews as hv


load_dotenv(".env")

# Initialize Panel with extensions for plotting
pn.extension('hvplot')

def save_plot(plot, filename="plot.png"):
    hv.save(plot, filename, fmt='png')

def image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def update_visualization(ticker, start, end, data_instruction):
    # Fetch the stock data from DuckDB
    data = get_data_from_duckdb_with_natural_language_query(data_instruction, 
                                                            ticker, 
                                                            start, 
                                                            end)

    # Generate the plot
    plot = data.hvplot.line('Date', stat_dic[data_instruction], 
                            width=800, height=400, 
                            title=f'{data_instruction} for {ticker}',
                            by='Ticker'
                            )
    
    # Save the plot
    save_plot(plot, "plot_image.png")
    
    # Display plot
    visualization_area.object = plot

    image_base64 = image_to_base64("plot_image.png")

    result = analyze_image_with_text(image_base64)
    print(result)


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
stat = ["Closing price", "Opening price", "Highest value of day", "Lowest of day"]
stat_dic = {"Closing price": "Close",
            "Opening price": "Open",
            "Highest value of day": "High",
            "Lowest value of day": "Low"}
# UI Components for stock selection
ticker_input = pn.widgets.MultiSelect(name='Stock Symbol', 
                                 value=stock_symbols[0:2], 
                                    options=stock_symbols,
                                 )
start_date = pn.widgets.DatePicker(name='Start Date', 
                                   value=pd.to_datetime('2022-01-01'))
end_date = pn.widgets.DatePicker(name='End Date', 
                                 value=pd.to_datetime('2024-01-01'))
instruction_input = pn.widgets.Select(name='Value',
                                      options = stat,
                                      value='Close'
                                      )

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
