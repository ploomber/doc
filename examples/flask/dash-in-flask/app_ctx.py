from flask import Flask, render_template_string, g
from utils import construct_dash_lists
import ssl
import pandas as pd

ssl._create_default_https_context = ssl._create_unverified_context

app = Flask(__name__)

with app.app_context():
    # Define Flask context variables to be used in apps
    g.df = pd.read_csv(
        "https://raw.githubusercontent.com/plotly/datasets/master/gapminder_unfiltered.csv"
    )

    # Obtain URL mapping of Dash apps and list items in template
    dash_url_mapping, list_items = construct_dash_lists(app)

    # Add Dash app to Flask context
    for dash_app in dash_url_mapping.values():
        app = dash_app

@app.route("/")
def hello_world():
    return render_template_string(f"""
    <h1>Main Flask App</h1>
    <h2>Select your Dash App</h2>
    <ul>
        {list_items}
    </ul>""")