from dash import Dash, html
import dash_bootstrap_components as dbc

app = Dash(__name__, external_stylesheets=[dbc.themes.MINTY])
server = app.server

app.layout = dbc.Container([
    dbc.Row(dbc.Col(html.H1('Welcome to Dash Customization Demo!', className='text-center my-4'), width=12)),
    dbc.Row(dbc.Col(dbc.Button('Click me!', color='primary', className='w-100 mt-4 mb-4'), width=12))
], fluid=True)

if __name__ == '__main__':
    app.run_server(debug=True)