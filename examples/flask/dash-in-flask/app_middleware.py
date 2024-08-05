from flask import Flask, render_template_string
from utils import construct_dash_lists
from werkzeug.middleware.dispatcher import DispatcherMiddleware

# Initialize Flask server
flask_app = Flask(__name__)

# List of Dash apps to add as middleware
dash_mw = {}

# Obtain URL mapping of Dash apps and list items in template
dash_url_mapping, list_items = construct_dash_lists()

# Integrate Flask and Dash apps using DispatcherMiddleware
app = DispatcherMiddleware(flask_app, dash_url_mapping)

@flask_app.route("/")
def index():
    return render_template_string(f"""
        <h1>Main Flask App</h1>
        <h2>Select your Dash App</h2>
        <ul>
            {list_items}
        </ul>""")
