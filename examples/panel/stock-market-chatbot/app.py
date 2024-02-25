import panel as pn
import hvplot.pandas
from chat import sql_query_generator
from stock import get_stock_data

# Initialize Panel with extensions
pn.extension('hvplot')

# UI Components
ticker_input = pn.widgets.TextInput(name='Stock Symbol', value='AAPL')
start_date = pn.widgets.DatePicker(name='Start Date')
end_date = pn.widgets.DatePicker(name='End Date')
instruction_input = pn.widgets.TextAreaInput(name='Instructions', height=100)
visualization_area = pn.pane.HoloViews()

# Callback for updating the visualization based on instructions
def update_visualization():
    ticker = ticker_input.value
    start = start_date.value
    end = end_date.value
    instructions = sql_query_generator(instruction_input.value)
    
    # Here, you would parse the instructions to understand what plot the user wants
    # For simplicity, let's assume the user always wants a closing price plot
    data = get_stock_data(ticker, start, end)
    plot = data.hvplot.line(x='Date', y='Close', width=800, height=400, title=f'{ticker} Closing Price')
    visualization_area.object = plot

def callback(input_text, user, instance: pn.chat.ChatInterface):
    """
    This function is called when the user sends a message
    """
    
    return sql_query_generator(input_text),update_visualization()


# Listen for changes in the instruction input
instruction_input.param.watch(update_visualization, 'value')

chat_interface = pn.chat.ChatInterface(callback=callback)
chat_interface.send(
    "Hello 😊 I am an OpenAI-powered assistant. \
        I can help answer questions about stock data",
    user="System",
    respond=False,
)
# Layout
layout = pn.Column(pn.Row(ticker_input, start_date, end_date), instruction_input, chat_interface,visualization_area)

pn.template.MaterialTemplate(
    title="<h4>GitHub Repository Searcher - <a href='https://ploomber.io/' target='_blank'> Hosted on Ploomber Cloud 🚀</a></h4>",
    logo="./images/logo-nb.png",
    main=[layout],
)
# Serve the Panel app
layout.servable()
