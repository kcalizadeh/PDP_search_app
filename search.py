import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import pandas as pd 
import pickle

from search_functions import *

external_stylesheets = [dbc.themes.CERULEAN]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)


# search bar
searchbar = html.Div(id="search-bar-container", children=
    [dbc.Row([
        dbc.Col(dcc.Dropdown(id="source-selection", 
                                  options=get_dropdown_list_search(),
                                  style={'width': '95%'},
                                  placeholder='Start typing to search...'), width=4),
        dbc.Col(dbc.Input(id="text-search-bar", 
                    placeholder="enter a word or phrase to search",
                    type='text',
                    n_submit=0,
                    autoFocus=True,
                    style={'width': '90%'}), width=5),
        dbc.Col(dbc.Button("SUBMIT", id="submit-button", color="primary", className="mr-1", n_clicks=0), width=1.8)
    ])
])

# overall layout
app.layout = html.Div([
    html.Br(),
    searchbar,
    html.Div(id="output", children=[])
])

@app.callback(Output(component_id="output", component_property="children"),
              [Input(component_id="submit-button", component_property="n_clicks"),
              Input(component_id="text-search-bar", component_property="n_submit"),
              Input(component_id="source-selection", component_property="value")],
              [State(component_id="text-search-bar", component_property="value")])
def search_df(n_clicks, n_submit, source, text):
    if source: 
        if n_clicks < 1 and n_submit < 1:
            return [html.Br(), html.P('Search results will appear here.')]
        if n_clicks > 0 or n_submit > 0:
                with open(f'slice_pickles/{source}_slice.pkl', 'rb') as df_pkl:
                    df = pickle.load(df_pkl)
                    results = df[df['SENTENCE'].str.contains('(?i)\s'+text+'\s')].copy()
                    results = results.sample(len(results))
                if len(results) == 0:
                    return 'Sorry, that word was not found in the selected source.'
                else:
                    try:
                        to_present = dash_table.DataTable(
                                                        id='table',
                                                        style_cell={
                                                                        'whiteSpace': 'normal',
                                                                        'height': 'auto',
                                                                        'lineHeight': '15px',
                                                                        'textAlign': 'left',
                                                                        'padding': '5px'
                                                                    },
                                                        
                                                        style_data_conditional=[
                                                            {
                                                                'if': {'column_id': 'TITLE'}, 
                                                                    'min_width':'200px'
                                                                },
                                                                {
                                                                'if': {'column_id':'AUTHOR'},
                                                                    'min_width':'80px'
                                                                },
                                                                {
                                                                'if': {'column_id':'SCHOOL'},
                                                                    'min_width':'80px'
                                                                }
                                                        ],
                                                        data=results.to_dict('records'),
                                                        columns=[{"name": i, "id": i} for i in df.columns],
                                                        page_action='native',
                                                        page_current= 0,
                                                        page_size= 15,
                                                    )
                
                    
                        return [html.Br(), html.P(f'Showing {len(results)} results for "{text}" in {source}.'), to_present]
                    except:
                        return 'Sorry, something went wrong.'





server = app.server

if __name__ == '__main__':
    app.config.suppress_callback_exceptions = True
    app.run_server(debug=True)         