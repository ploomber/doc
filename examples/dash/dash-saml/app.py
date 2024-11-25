import json
import dash
from dash import Dash, Input, Output, html, dcc
import flask
from server import COOKIE_NAME, server
import dash_material_ui as mui

dash._dash_renderer._set_react_version("18.2.0")

app = Dash(__name__, server=False)
app.init_app(server)

app.layout = html.Div([
    dcc.Location(id='url'),
    html.H1('Dash - SAML Auth', style={'textAlign': 'center', 'color': '#1976d2', 'marginBottom': '2rem'}),
    html.Div([
        mui.Button(id="login_button", children="Login", variant="contained"),
        mui.Button(
            id="logout_button", children="Logout", variant="outlined",
        ),
        dcc.Location(id="url_login"),
        dcc.Location(id="url_logout")
    ], style={'display': 'flex', 'gap': '1rem', 'marginBottom': '1rem', 'justifyContent': 'center'}),

    mui.Alert(
        id="user_display",
        variant="filled",
        severity="info",
    ),
    dash.page_container,
])


@app.callback(
    Output("url_login", "pathname"),
    Input("login_button", "n_clicks"),
    prevent_initial_call=True
)
def redirect_to_login(n_clicks):
    return "/login"


@app.callback(
    Output("url_logout", "pathname"),
    Input("logout_button", "n_clicks"),
    prevent_initial_call=True
)
def redirect_to_logout(n_clicks):
    return "/logout"


@app.callback(
    [Output("user_display", "children"),
     Output("user_display", "severity")],
    Input('url', 'pathname')
)
def update_user_display(pathname, request=flask.request):
    user = request.cookies.get(COOKIE_NAME)

    if user:
        user = json.loads(user)
        email = user["attributes"]["http://schemas.xmlsoap.org/ws/2005/05/identity/claims/emailaddress"]
        return f"You are connected as: {email[0]}", "success"
    else:
        return "Please login", "warning"


if __name__ == '__main__':
    app.run(debug=True)
