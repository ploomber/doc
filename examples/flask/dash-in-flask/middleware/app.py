from flask import Flask, render_template_string, g
from dash_apps import simple_app, population
from werkzeug.middleware.dispatcher import DispatcherMiddleware
import pandas as pd

# Setup Dash apps. 
# For key, use your preferred URL for app.
# For value, add initialization function and app name for each app
DASH_APPS_ = {
    '/simple': (simple_app.init_app, "Simple App"),
    '/population': (population.init_app, "Population App")
}

# Initialize Flask server
flask_app = Flask(__name__)

with flask_app.app_context():
    # Define Flask context variables to be used in apps. 
    # In this case, we define the dataframe used in the Population app (df)
    # and the Flask instance to be passed to both apps (cur_app)
    g.df = pd.read_csv(
        "https://raw.githubusercontent.com/plotly/datasets/master/gapminder_unfiltered.csv"
    )
    
    # List of Dash apps to add as middleware
    dash_mw_input = {}

    # <li> in the template: URLs to each dash app
    list_items = ""

    for url in DASH_APPS_:
        dash_mw_input[url] = DASH_APPS_[url][0](url + "/")
        list_items += "<li><a href=\"" + url + "/\">" + DASH_APPS_[url][1] + "</a></li>\n"

    # Integrate Flask and Dash apps using DispatcherMiddleware
    # The app becomes a Middleware instance, which will default to the 
    # routes in the Flask app if the URL is not found among the mounted
    # Dash apps
    app = DispatcherMiddleware(flask_app, dash_mw_input)

@flask_app.route("/")
def index():
    return render_template_string(f"""
        <h1>Main Flask App</h1>
        <h2>Select your Dash App</h2>
        <ul>
            {list_items}
        </ul>""")
