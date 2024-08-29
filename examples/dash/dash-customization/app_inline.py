from dash import html, Dash

app = Dash(__name__)
server = app.server

app.layout = html.Div([
    html.H1(
        'Welcome to Dash Customization Demo!',
        style={'textAlign': 'center'}
    ),
    html.Button(
        'Click me 1!',
        style={
            'width': '100%',
            'padding': '10px',
            'background': 'darkgreen',
            'color': 'white',
            'fontSize': '16px'
        }
    ),
    html.Button(
        'Click me 2!',
        style={
            'width': '100%',
            'padding': '10px',
            'background': 'blue',
            'color': 'white',
            'fontSize': '16px'
        }
    ),
    html.Button(
        'Click me 3!',
        style={
            'width': '100%',
            'padding': '10px',
            'background': 'red',
            'color': 'white',
            'fontSize': '16px'
        }
    )
], style={'padding': '20px'})

if __name__ == '__main__':
    app.run_server(debug=True)
