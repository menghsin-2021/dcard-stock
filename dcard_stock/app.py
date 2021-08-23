import dash
import dash_html_components as html
import dash_core_components as dcc
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from dash.dependencies import Input, Output

# Load data
df_total_like_count = pd.read_csv('data/df_posts_total_like_count.csv', index_col=0, parse_dates=True)
df_total_like_count_shipping = pd.read_csv('data/df_posts_total_like_count_shipping.csv', index_col=0, parse_dates=True)
df_2603 = pd.read_csv('data/df_2603_price_20201121.csv', index_col=0, parse_dates=True)
df_2609 = pd.read_csv('data/df_2609_price_20201121.csv', index_col=0, parse_dates=True)
df_2615 = pd.read_csv('data/df_2615_price_20201121.csv', index_col=0, parse_dates=True)

# load css
# Dash will automatically load any .css-file placed in a folder named assets.

# Initialize the app
app = dash.Dash(__name__)
app.config.suppress_callback_exceptions = True


# 建立選擇個股清單
list_stocks = [2603, 2609, 2615, 'shipping']

def get_options(list_stocks):
    dict_list = []
    for i in list_stocks:
        dict_list.append({'label': i, 'value': i})

    return dict_list


# 總讚數圖 (無篩選)
fig_total_like = go.Figure()
# Add traces
fig_total_like.add_trace(go.Scatter(x=df_total_like_count.index,
                         y=df_total_like_count['total_like_count'],
                         mode='lines',
                         opacity=0.7,
                         name='當日總讚數',
                         textposition='bottom center'))

fig_total_like.add_trace(go.Scatter(x=df_total_like_count_shipping.index,
                         y=df_total_like_count_shipping['total_like_count'],
                         mode='lines',
                         opacity=0.7,
                         name="提及航運關鍵字貼文當日總讚數",
                         textposition='bottom center'))

fig_total_like.update_layout(
              colorway=['#375CB1', '#FF7400', '#FFF400', '#FF0056', "#5E0DAC", '#FF4F00'],
              template='plotly_dark',
              paper_bgcolor='rgba(0, 0, 0, 0)',
              plot_bgcolor='rgba(0, 0, 0, 0)',
              margin={'b': 15},
              hovermode='x',
              autosize=True,
              title={'text': '股票板 (自從開板以來) 的活躍度 (無關鍵字篩選 vs 航運類股關鍵字篩選)', 'font': {'color': 'white'}, 'x': 0.5},
              xaxis={'range': [df_total_like_count.index.min(), df_total_like_count.index.max()]},
          )

# Callback for timeseries price
@app.callback(Output('timeseries', 'figure'),
              [Input('stockselector', 'value')])
def update_graph(selected_dropdown_value):  # 把 stockselector 的 value 投進去(結構為 list)
    # Create figure with secondary y-axis
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Add traces
    if 'shipping' in selected_dropdown_value:
        fig.add_trace(
            go.Scatter(x=df_total_like_count_shipping.index,
                       y=df_total_like_count_shipping['total_like_count'],
                       mode='lines',
                       opacity=0.7,
                       name='提及航運關鍵字貼文當日總讚數',
                       textposition='bottom center'),
            secondary_y=False,
        )

    if 2603 in selected_dropdown_value:
        fig.add_trace(
            go.Scatter(x=df_2603.index,
                       y=df_2603['收盤價'],
                       mode='lines',
                       opacity=0.7,
                       name='2603當日收盤價',
                       textposition='bottom center'),
            secondary_y=True,
        )

    if 2609 in selected_dropdown_value:
        fig.add_trace(go.Scatter(x=df_2609.index,
                                 y=df_2609['收盤價'],
                                 mode='lines',
                                 opacity=0.7,
                                 name='2609當日收盤價',
                                 textposition='bottom center'),
                      secondary_y=True)

    if 2615 in selected_dropdown_value:
        fig.add_trace(go.Scatter(x=df_2615.index,
                                 y=df_2615['收盤價'],
                                 mode='lines',
                                 opacity=0.7,
                                 name='2615當日收盤價',
                                 textposition='bottom center'),
                      secondary_y=True)

    fig.update_layout(
                  colorway=['#375CB1', '#FF7400', '#FFF400', '#FF0056', "#5E0DAC", '#FF4F00'],
                  template='plotly_dark',
                  paper_bgcolor='rgba(0, 0, 0, 0)',
                  plot_bgcolor='rgba(0, 0, 0, 0)',
                  margin={'b': 15},
                  hovermode='x',
                  autosize=True,
                  title={'text': '航運類股當日收盤價 vs 提及航運關鍵字貼文當日總讚數', 'font': {'color': 'white'}, 'x': 0.5},
                  xaxis={'range': [df_total_like_count.index.min(), df_total_like_count.index.max()]},
              ),

    return fig


# HTML
app.layout = html.Div(
    children=[
        html.Div(className='row',  # define the row element
                 children=[
                    html.Div(className='three columns div-user-controls',  # define the left element
                             children=[
                                 html.H2('DASH - STOCK PRICES'),
                                 html.P('Visualising time series with Plotly - Dash.'),
                                 html.P('Pick one or more stocks from the dropdown below.'),
                                 html.Div(
                                     className='div-for-dropdown',
                                     children=[
                                         dcc.Dropdown(id='stockselector', options=get_options(list_stocks=list_stocks),
                                                      multi=True, value=list_stocks,
                                                      style={'backgroundColor': '#1E1E1E'},
                                                      className='stockselector'
                                                      ),
                                     ],
                                     style={'color': '#1E1E1E'})
                                ]
                             ),
                    html.Div(className='nine columns div-for-charts bg-grey',  # define the right element
                             children=[
                                 dcc.Graph(id='timeseries', config={'displayModeBar': False}, animate=True),
                                 dcc.Graph(id='timeseries2', figure=fig_total_like, config={'displayModeBar': False}, animate=True)
                             ])
                              ])
        ]

)


# run
if __name__ == '__main__':
    app.run_server(debug=True)