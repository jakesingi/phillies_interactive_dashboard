# -*- coding: utf-8 -*-
# link to github
# imports
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


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server


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

# All statistics from the original spin_evaluation.csv
baseline_spin = df2['baseline_spin']
new_tech_spin = df2['new_tech_spin']
corr2 = df2['baseline_spin'].corr(df2['new_tech_spin'])
df2['abs_errors'] = np.abs(df2['baseline_spin'] - df2['new_tech_spin'])
MAE = np.mean(df2['abs_errors'])
percent_in_range = sum((df2['new_tech_spin'] >= df2['baseline_spin'] - MAE) & (df2['new_tech_spin'] <= df2['baseline_spin'] + MAE))/df2.shape[0]

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

    The plot below is a scatterplot of the original data given in `spin_evaluation.csv`. We can see all of the overestimation and underestimation 
    problems I mentioned in my initial report. The correlation given is the correlation between the baseline technology's readings and the
    new technology's readings. This could be useful if, for example, the new technology readings suddenly become very closely correlated with the baseline readings. Then, one could apply a small linear transformation to the new tech readings to get to the appropriate baseline readings. The "Percent in MAE Range" is the proportion of the new technology's readings that fall within the baseline reading
    plus/minus the MAE. This metric is the most important one in determining the reliability of the new technology. For example, a reading of 81%, which we see in the default plot, implies that on average, for every 5 pitches measured by the new technology, about 1 will differ substantially (plus/minus 61.5 RPM) from the measurement given by the baseline technology.
    '''),
    
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
                xaxis={'type': 'log', 'title': "Baseline Spin (RPM)"},
                yaxis={'title': "New Tech Spin (RPM)"},
                margin={'l': 80, 'b': 40, 't': 0, 'r': 80},
                legend={'x': 0, 'y': 1},
                hovermode='closest'
            )
        }
    ),
    html.H3(
        children=f"Correlation: {np.round(corr2, 4)}",
        style={
            'textAlign': 'center',
            'color': colors['black']
        }
    ),
    html.H3(
        children=f"MAE: {np.round(MAE, 4)}",
        style={
            'textAlign': 'center',
            'color': colors['black']
        }
    ),
    html.H3(
        children=f"Percent in MAE Range: {np.round(percent_in_range, 4)}",
        style={
            'textAlign': 'center',
            'color': colors['black']
        }
    ),
    
    dcc.Markdown(
    '''
    #### Uploading New Data

    Upload a csv file here in the same format as the original `spin_evaluations.csv` in order to make comparisons. A scatterplot will be generated
    along with the correlation, MAE, and "Percent in MAE Range" statistics described above. Remember that you can upload multiple files!
    '''),
    
    
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
    
    corr = df.iloc[:, 2].corr(df.iloc[:, 1])
    df['abs_errors'] = np.abs(df['baseline_spin'] - df['new_tech_spin'])
    MAE2 = np.mean(df['abs_errors'])
    percent_in_range2 = sum((df['new_tech_spin'] >= df['baseline_spin'] - MAE2) & (df['new_tech_spin'] <= df['baseline_spin'] + MAE2))/df.shape[0]
    
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
                xaxis={'type': 'log', 'title': df.iloc[:, 2].name + " (RPM)"},
                yaxis={'title': df.iloc[:, 1].name + " (RPM)"},
                margin={'l': 80, 'b': 40, 't': 0, 'r': 80},
                legend={'x': 0, 'y': 1},
                hovermode='closest'
            )
        }
        ),
        html.H3(
        children=f"Correlation: {np.round(corr, 4)}",
        style={
            'textAlign': 'center',
            'color': colors['black']
        }
    ),
        html.H3(
        children=f"MAE: {np.round(MAE2, 4)}",
        style={
            'textAlign': 'center',
            'color': colors['black']
        }
    ),
        html.H3(
        children=f"Percent in MAE Range: {np.round(percent_in_range2, 4)}",
        style={
            'textAlign': 'center',
            'color': colors['black']
        }
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
    
    
    

    
    

if __name__ == '__main__':
    app.run_server(debug=True)