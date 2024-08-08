from flask import Flask, render_template_string, g
import ssl
import pandas as pd
from dash_apps import simple_app, population

ssl._create_default_https_context = ssl._create_unverified_context

# Setup Dash apps. 
# For key, use your preferred URL for app.
# For value, add initialization function and app name for each app
DASH_APPS_ = {
    '/simple_app': (simple_app.init_app, "Simple App"),
    '/population': (population.init_app, "Population App")
}

app = Flask(__name__)

with app.app_context():
    # Define Flask context variables to be used in apps. 
    # In this case, we define the dataframe used in the Population app (df)
    # and the Flask instance to be passed to both apps (cur_app)
    g.df = pd.read_csv(
        "https://raw.githubusercontent.com/plotly/datasets/master/gapminder_unfiltered.csv"
    )

    g.cur_app = app
    
    # <li> in the template: URLs to each dash app
    list_items = ""

    for url in DASH_APPS_:
        # Add Dash app to Flask context
        app = DASH_APPS_[url][0](url + "/")
        list_items += "<li><a href=\"" + url + "/\">" + DASH_APPS_[url][1] + "</a></li>\n"

@app.route("/")
def home():
    return render_template_string(f"""
        <h1>Main Flask App</h1>
        <h2>Select your Dash App</h2>
        <ul>
            {list_items}
        </ul>"""
    )
