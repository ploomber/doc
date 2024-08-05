from dash_apps import dash1, dash2

# Setup Dash apps. 
# For key, use your preferred URL for app.
# For value, add initialization function and app name for each app
DASH_APPS_ = {
    '/app1': (dash1.init_app, "Simple App"),
    '/app2': (dash2.init_app, "Population App")
}

def construct_dash_lists(app=None):
    """Return a dictionary of URLs mapped to Dash apps, and a string HTML list items, 
    each being a link to the Dash app corresponding to its name."""
    # List of Dash apps to add as middleware
    dash_url_mapping = {}

    # List items in the template: URLs to each dash app
    list_items = ""

    for url in DASH_APPS_:
        dash_url_mapping[url] = DASH_APPS_[url][0](url + "/", app)
        list_items += "<li><a href=\"" + url + "/\">" + DASH_APPS_[url][1] + "</a></li>\n"

    return dash_url_mapping, list_items
