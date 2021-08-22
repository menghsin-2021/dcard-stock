import dash
import dash_html_components as html
import dash_core_components as dcc
import plotly.graph_objects as go
import pandas as pd
from dash.dependencies import Input, Output

# Load data
df_total_like_count = pd.read_csv('data/df_posts_total_like_count.csv', index_col=0, parse_dates=True)
df_total_like_count_shipping = pd.read_csv('data/df_posts_total_like_count_shipping.csv', index_col=0, parse_dates=True)
df_2603 = pd.read_csv('data/df_2603_price_20201121.csv', index_col=0, parse_dates=True)
df_2609 = pd.read_csv('data/df_2609_price_20201121.csv', index_col=0, parse_dates=True)
df_2615 = pd.read_csv('data/df_2615_price_20201121.csv', index_col=0, parse_dates=True)
df.index = pd.to_datetime(df['Date'])

# load css
# Dash will automatically load any .css-file placed in a folder named assets.

# Initialize the app
app = dash.Dash(__name__)
app.config.suppress_callback_exceptions = True

list_stocks = [2603, 2609, 2615]

def get_options(list_stocks):
    dict_list = []
    for i in list_stocks:
        dict_list.append({'label': i, 'value': i})

    return dict_list


app.layout = html.Div(
    children=[
        html.Div(className='row',  # define the row element
                 children=[
                    html.Div(className='four columns div-user-controls',  # define the left element
                             children=[
                                 html.H2('DASH - STOCK PRICES'),
                                 html.P('Visualising time series with Plotly - Dash.'),
                                 html.P('Pick one or more stocks from the dropdown below.'),
                                 html.Div(
                                     className='div-for-dropdown',
                                     children=[
                                         dcc.Dropdown(id='stockselector', options=get_options(df['stock'].unique()),
                                                      multi=True, value=[df['stock'].sort_values()[0]],
                                                      style={'backgroundColor': '#1E1E1E'},
                                                      className='stockselector'
                                                      ),
                                     ],
                                     style={'color': '#1E1E1E'})
                                ]
                             ),
                    html.Div(className='eight columns div-for-charts bg-grey',  # define the right element
                             children=[
                                 dcc.Graph(id='timeseries', config={'displayModeBar': False}, animate=True),
                                 dcc.Graph(id='timeseries2', config={'displayModeBar': False}, animate=True),
                                 dcc.Graph(id='timeseries3', config={'displayModeBar': False}, animate=True)
                             ])
                              ])
        ]

)


# Callback for timeseries price
@app.callback(Output('timeseries', 'figure'),
              [Input('stockselector', 'value')])
def update_graph(selected_dropdown_value):  # 把 stockselector 的 value 投進去(結構為 list)
    trace1 = []
    df_sub = df
    for stock in selected_dropdown_value:
        trace1.append(go.Scatter(x=df_sub[df_sub['stock'] == stock].index,
                                 y=df_sub[df_sub['stock'] == stock]['value'],
                                 mode='lines',
                                 opacity=0.7,
                                 name=stock,
                                 textposition='bottom center'))
    traces = [trace1]
    data = [val for sublist in traces for val in sublist]
    figure = {'data': data,
              'layout': go.Layout(
                  colorway=["#5E0DAC", '#FF4F00', '#375CB1', '#FF7400', '#FFF400', '#FF0056'],
                  template='plotly_dark',
                  paper_bgcolor='rgba(0, 0, 0, 0)',
                  plot_bgcolor='rgba(0, 0, 0, 0)',
                  margin={'b': 15},
                  hovermode='x',
                  autosize=True,
                  title={'text': 'Stock Prices', 'font': {'color': 'white'}, 'x': 0.5},
                  xaxis={'range': [df_sub.index.min(), df_sub.index.max()]},
              ),

              }

    return figure


if __name__ == '__main__':
    app.run_server(debug=True)