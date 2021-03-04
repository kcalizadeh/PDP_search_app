import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import pandas as pd 
import pickle
import psycopg2
import os

from search_functions import *

external_stylesheets = [dbc.themes.CERULEAN]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

classifier_dict = {'Plato': 'SCHOOL', 'Aristotle': 'SCHOOL', 'Locke': 'AUTHOR', 'Hume': 'AUTHOR', 'Berkeley': 'AUTHOR', 'Spinoza': 'AUTHOR', 'Leibniz': 'AUTHOR', 'Descartes': 'AUTHOR', 'Malebranche': 'AUTHOR', 'Russell': 'AUTHOR', 'Moore': 'AUTHOR', 'Wittgenstein': 'AUTHOR', 'Lewis': 'AUTHOR', 'Quine': 'AUTHOR', 'Popper': 'AUTHOR', 'Kripke': 'AUTHOR', 'Foucault': 'AUTHOR', 'Derrida': 'AUTHOR', 'Deleuze': 'AUTHOR', 'Merleau-Ponty': 'AUTHOR', 'Husserl': 'AUTHOR', 'Heidegger': 'AUTHOR', 'Kant': 'AUTHOR', 'Fichte': 'AUTHOR', 'Hegel': 'AUTHOR', 'Marx': 'AUTHOR', 'Lenin': 'AUTHOR', 'Smith': 'AUTHOR', 'Ricardo': 'AUTHOR', 'Keynes': 'AUTHOR', 'Epictetus': 'AUTHOR', 'Marcus Aurelius': 'AUTHOR', 'Plato - Complete Works': 'TITLE', 'Aristotle - Complete Works': 'TITLE', 'Second Treatise On Government': 'TITLE', 'Essay Concerning Human Understanding': 'TITLE', 'A Treatise Of Human Nature': 'TITLE', 'Dialogues Concerning Natural Religion': 'TITLE', 'Three Dialogues': 'TITLE', 'A Treatise Concerning The Principles Of Human Knowledge': 'TITLE', 'Ethics': 'TITLE', 'On The Improvement Of Understanding': 'TITLE', 'Theodicy': 'TITLE', 'Discourse On Method': 'TITLE', 'Meditations On First Philosophy': 'TITLE', 'The Search After Truth': 'TITLE', 'The Analysis Of Mind': 'TITLE', 'The Problems Of Philosophy': 'TITLE', 'Philosophical Studies': 'TITLE', 'Philosophical Investigations': 'TITLE', 'Tractatus Logico-Philosophicus': 'TITLE', 'Lewis - Papers': 'TITLE', 'Quintessence': 'TITLE', 'The Logic Of Scientific Discovery': 'TITLE', 'Naming And Necessity': 'TITLE', 'Philosophical Troubles': 'TITLE', 'On Certainty': 'TITLE', 'The Birth Of The Clinic': 'TITLE', 'Madness And Civilization': 'TITLE', 'The Order Of Things': 'TITLE', 'Writing And Difference': 'TITLE', 'Difference And Repetition': 'TITLE', 'Anti-Oedipus': 'TITLE', 'The Phenomenology Of Perception': 'TITLE', 'The Crisis Of The European Sciences And Phenomenology': 'TITLE', 'The Idea Of Phenomenology': 'TITLE', 'Being And Time': 'TITLE', 'Off The Beaten Track': 'TITLE', 'Critique Of Practical Reason': 'TITLE', 'Critique Of Judgement': 'TITLE', 'Critique Of Pure Reason': 'TITLE', 'The System Of Ethics': 'TITLE', 'Science Of Logic': 'TITLE', 'The Phenomenology Of Spirit': 'TITLE', 'Elements Of The Philosophy Of Right': 'TITLE', 'Capital': 'TITLE', 'The Communist Manifesto': 'TITLE', 'Essential Works Of Lenin': 'TITLE', 'The Wealth Of Nations': 'TITLE', 'On The Principles Of Political Economy And Taxation': 'TITLE', 'A General Theory Of Employment, Interest, And Money': 'TITLE', 'Enchiridion': 'TITLE', 'Meditations': 'TITLE', 'Empiricism': 'SCHOOL', 'Rationalism': 'SCHOOL', 'Analytic': 'SCHOOL', 'Continental': 'SCHOOL', 'Phenomenology': 'SCHOOL', 'German Idealism': 'SCHOOL', 'Communism': 'SCHOOL', 'Capitalism': 'SCHOOL', 'Stoicism': 'SCHOOL'}

# DATABASE_URL = os.environ['DATABASE_URL']


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
    # if source: 
        if n_clicks < 1 and n_submit < 1:
            return [html.Br(), html.P(f'Search results will appear here.')]
        if n_clicks > 0 or n_submit > 0:
            # read database connection url from the enivron variable we just set.
            con = None
            DATABASE_URL = os.environ.get('HEROKU_POSTGRESQL_BROWN_URL')

            try:
                # create a new database connection by calling the connect() function
                con = psycopg2.connect(DATABASE_URL)

                #  create a new cursor author = '{source}'
                cur = con.cursor()
                
                source_type = classifier_dict[source].title()

                query = f"""SELECT * 
                            FROM phil_nlp 
                            WHERE "{source_type.upper()}" = '{source}' AND "SENTENCE" LIKE '% {text} %'
                                """
                
                results = pd.read_sql(query, con)

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
                                                        columns=[{"name": i, "id": i} for i in results.columns],
                                                        page_action='native',
                                                        page_current= 0,
                                                        page_size= 15,
                                                    )
                
                    
                # return DATABASE_URL
                # close the communication with the HerokuPostgres
                return [html.Br(), html.P(f'Showing {len(results)} results for "{text}" in {source}.'), to_present]
                # return(cur.fetchone())
            except Exception as error:
                print('Cause: {}'.format(error))

            finally:
                # close the communication with the database server by calling the close()
                if con is not None:
                    con.close()





server = app.server

if __name__ == '__main__':
    app.config.suppress_callback_exceptions = True
    app.run_server(debug=True)         


