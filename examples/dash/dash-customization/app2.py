from dash import html, Dash

app = Dash(__name__)
server = app.server

app.layout = html.Div([
    html.H1('Welcome to Dash Customization Demo!', className='header'),
    html.Button('Click me!', className='button')
], className='container')

if __name__ == '__main__':
    app.run_server(debug=True)