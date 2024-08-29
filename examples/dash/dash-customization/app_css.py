from dash import html, Dash

app = Dash(__name__)
server = app.server

app.layout = html.Div([
    html.H1(
        'Welcome to Dash Customization Demo!',
        className='center-text'
    ),
    html.Button('Click me 1!', className='button green'),
    html.Button('Click me 2!', className='button blue'),
    html.Button('Click me 3!', className='button red')
], className='padding-20')

if __name__ == '__main__':
    app.run_server(debug=True)
