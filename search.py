import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc


external_stylesheets = [dbc.themes.CERULEAN]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)


# overall layout
app.layout = html.Div([
    html.H1('hello')
])


server = app.server

if __name__ == '__main__':
    app.config.suppress_callback_exceptions = True
    app.run_server(debug=True)         