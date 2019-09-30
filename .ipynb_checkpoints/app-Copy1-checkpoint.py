# -*- coding: utf-8 -*-
import base64
import datetime
import io
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import pandas as pd
import plotly.graph_objs as go
import numpy as np
import dash_table

df = pd.read_csv(
    'https://gist.githubusercontent.com/chriddyp/' +
    '5d1ea79569ed194d432e56108a04d188/raw/' +
    'a9f9e8076b837d541398e999dcbac2b2826a81f8/'+
    'gdp-life-exp-2007.csv')

df2 = pd.read_csv("spin_evaluation.csv").iloc[:, 1:3]
columns = [i for i in df2.columns.values]

def generate_table(dataframe, max_rows=10):
    return html.Table(
        # Header
        [html.Tr([html.Th(col) for col in dataframe.columns])] +

        # Body
        [html.Tr([
            html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
        ]) for i in range(min(len(dataframe), max_rows))]
    )





external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

colors = {
    'background': '#111111',
    'text': '#7FDBFF',
    'phillies': '#E81828',
    'white': '#FFFFFF',
    'black': '#000000'
}

markdown_text = '''
### Dash and Markdown

Dash apps can be written in Markdown.
Dash uses the [CommonMark](http://commonmark.org/)
specification of Markdown.
Check out their [60 Second Markdown Tutorial](http://commonmark.org/help/)
if this is your first introduction to Markdown!
'''
baseline_spin = df2['baseline_spin']
new_tech_spin = df2['new_tech_spin']
x = np.linspace(800, 3000, 2200)
y = x


app.layout = html.Div(style={'backgroundColor': colors['white']}, children=[
    
    html.H1(
        children="Phillies: Evaluating New Pitch-Tracking Technology",
        style={
            'textAlign': 'center',
            'color': colors['phillies']
        }
    ),

    html.Div(children='Author: Jake Singleton', style={
        'textAlign': 'center',
        'color': colors['black']
    }),
    
    dcc.Markdown(
    '''
    #### Interactive Dashboard for Visualizing New Technology's Performance

    Upload a spin_e
    '''),
    
    dcc.Tabs(id="tabs", value='tab-1', children=[
        dcc.Tab(label='Tab one', value='tab-1'),
        dcc.Tab(label='Tab two', value='tab-2'),
    ]),
    html.Div(id='tabs-content'),
    
    
    dcc.Upload(
        id='upload-data',
        children=html.Div([
            'Drag and Drop or ',
            html.A('Select Files')
        ]),
        style={
            'width': '100%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '10px'
        },
        # Allow multiple files to be uploaded
        multiple=True
    ),
    html.Div(id='output-data-upload')
])


def parse_contents(contents, filename, date):
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')))
        elif 'xls' in filename:
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(decoded))
    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ])

    return html.Div([
        html.H5(filename),
        html.H6(datetime.datetime.fromtimestamp(date)),

        
        dcc.Graph(
        id='jake',
        figure={
            'data': [
                go.Scatter(
                    x=df.iloc[:, 2],
                    y=df.iloc[:, 1],
                    text="(Baseline, New Tech)",
                    mode='markers',
                    opacity=0.7,
                    marker={
                        'size': 15,
                        'line': {'width': 0.5, 'color': 'white'}
                    }
                ) 
            ],
            'layout': go.Layout(
                xaxis={'type': 'log', 'title': df.iloc[:, 2].name},
                yaxis={'title': df.iloc[:, 1].name},
                margin={'l': 80, 'b': 40, 't': 0, 'r': 80},
                legend={'x': 0, 'y': 1},
                hovermode='closest'
            )
        }
    ),
        
        dash_table.DataTable(
            data=df.head().to_dict('records'),
            columns=[{'name': i, 'id': i} for i in df.columns]
        ),

        html.Hr(),  # horizontal line

        # For debugging, display the raw contents provided by the web browser
        html.Div('Raw Content'),
        html.Pre(contents[0:200] + '...', style={
            'whiteSpace': 'pre-wrap',
            'wordBreak': 'break-all'
        })
    ])


@app.callback(Output('output-data-upload', 'children'),
              [Input('upload-data', 'contents')],
              [State('upload-data', 'filename'),
               State('upload-data', 'last_modified')])

def update_output(list_of_contents, list_of_names, list_of_dates):
    if list_of_contents is not None:
        children = [
            parse_contents(c, n, d) for c, n, d in
            zip(list_of_contents, list_of_names, list_of_dates)]
        return children
    
    
    
@app.callback(Output('tabs-content', 'children'),
              [Input('tabs', 'value')])
def render_content(tab):
    if tab == 'tab-1':
        return html.Div([
            html.H3('Tab content 1'),
            
            dcc.Graph(
        id='jake',
        figure={
            'data': [
                go.Scatter(
                    x=df2['baseline_spin'],
                    y=df2['new_tech_spin'],
                    text="(Baseline, New Tech)",
                    mode='markers',
                    opacity=0.7,
                    marker={
                        'size': 15,
                        'line': {'width': 0.5, 'color': 'white'}
                    }
                ) 
            ],
            'layout': go.Layout(
                xaxis={'type': 'log', 'title': "Baseline Spin"},
                yaxis={'title': "New Tech Spin"},
                margin={'l': 80, 'b': 40, 't': 0, 'r': 80},
                legend={'x': 0, 'y': 1},
                hovermode='closest'
            )
        }
    )
        ])
    elif tab == 'tab-2':
        return html.Div([
            html.H3('Tab content 2')
        ])
    
    
    

if __name__ == '__main__':
    
    app.run_server(debug=True)