import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px
import sys
import datetime as dt

sys.path.append(r'C:\Users\MichaelSchwarz\PycharmProjects\FinanceProjects')
import MyFuncGeneral as my

# PREPARE TAB1 STOCKS RELATIVE
sys.path.append(r'C:/Users/MichaelSchwarz/PycharmProjects/FinanceProjects/StockSelection')
import CompanyClass as c


# get the tickers to display
def get_tickerdata_for_display(start, end):
    cnx = my.cnx_mysqldb('fuyu')
    query = "select * from issues_yh_now_selected"
    comps = pd.read_sql(query, con=cnx)
    c.Company.remove_all_companies()  # remove all companies before new ones are created!
    for i in comps['Ticker_yahoo']:
        i = c.Company(i)
    dat = i.compare(start, end)
    return dat
    # example
    # start="2017-01-05"; end="2020-05-25"
    # get_tickerdata_for_display (start,end)


default_start = dt.date.today() - dt.timedelta(days=3 * 365)
default_end = dt.date.today()
# PREPARE TAB2 PORTFOLIO
sys.path.append(r'C:/Users/MichaelSchwarz/PycharmProjects/FinanceProjects/PortfolioConstruction')
import evaluate_portfolio_exposure as epe

# dropdown menu
# get the different Clusternames as Options for the Dropdown Choice for SunburstCluster Center
cnx = my.cnx_mysqldb('fuyu')
query = "select distinct NameMotherCluster from ( " + \
        "select level1 as NameMotherCluster from exposure_clusters_by_level " + \
        "union select '__________LEVEL2_________' union select distinct level2 from exposure_clusters_by_level )s " + \
        "where NameMotherCluster is not null"
dropdownLabClusters = pd.read_sql(query, con=cnx)
optionsmenu_own = [dict(label=i, value=i) for i in dropdownLabClusters["NameMotherCluster"]]

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
# APP START
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div([

    dcc.Tabs(id='tabs-example', value='tab-1', children=[
        dcc.Tab(label='Stocks Relative', value='tab-1'),
        dcc.Tab(label='Portfolio', value='tab-2'),
    ]),
    html.Div(id='tabs-example-content')
])


@app.callback(Output('tabs-example-content', 'children'),
              [Input('tabs-example', 'value')])
def render_content(tab):
    if tab == 'tab-1':
        fig = get_tickerdata_for_display(start=default_start, end=default_end)
        fig.update_layout(
            # title_text="Time series with range slider and selectors",
            xaxis=dict(
                rangeselector=dict(
                    buttons=list([
                        dict(count=1,
                             label="1m",
                             step="month",
                             stepmode="backward"),
                        dict(count=6,
                             label="6m",
                             step="month",
                             stepmode="backward"),
                        dict(count=1,
                             label="YTD",
                             step="year",
                             stepmode="todate"),
                        dict(count=1,
                             label="1y",
                             step="year",
                             stepmode="backward"),
                        dict(step="all")
                    ])
                ),
                rangeslider=dict(
                    visible=True
                ),
                type="date"
            ))
        return html.Div([
            dcc.Markdown('''
            #### Dash and Markdown
            explain here in markdown what you can see!
            '''),
            # html.H3('Performance over time'),
            html.Div([
            dcc.DatePickerSingle(id='set-start-date-id', initial_visible_month=default_start, date=default_start),
            # .format(date)),
            html.P('Start and Normalize by Date')
            ]),
            dcc.Graph(id='stocks_rel', figure=fig)
        ])

    elif tab == 'tab-2':
        return html.Div([
            html.H3('Composition by different Clusters'),
            dcc.Dropdown(
                id='dropdown-id',
                options=optionsmenu_own,
                value='GICS'
            ),
            # dcc.Textarea(id='text', value="test"),
            dcc.Graph(id='graph-portfolio-view')
        ])


@app.callback(
    dash.dependencies.Output('stocks_rel', 'figure'),
    [dash.dependencies.Input('set-start-date-id', 'date')]
)
def update_output_div(new_start):
    fig = get_tickerdata_for_display(start=new_start, end=default_end)
    fig.update_layout(
        # title_text="Time series with range slider and selectors",
        xaxis=dict(
            rangeselector=dict(
                buttons=list([
                    dict(count=1,
                         label="1m",
                         step="month",
                         stepmode="backward"),
                    dict(count=6,
                         label="6m",
                         step="month",
                         stepmode="backward"),
                    dict(count=1,
                         label="YTD",
                         step="year",
                         stepmode="todate"),
                    dict(count=1,
                         label="1y",
                         step="year",
                         stepmode="backward"),
                    dict(step="all")
                ])
            ),
            rangeslider=dict(
                visible=True
            ),
            type="date"
        )
    )
    return fig


@app.callback(
    dash.dependencies.Output('graph-portfolio-view', 'figure'),
    [dash.dependencies.Input('dropdown-id', 'value')]
)
def update_output_div(chosen_cluster):
    clust = epe.cluster_data_for_sunburst_eval(chosen_cluster)
    f = px.sunburst(clust,
                    names='child',
                    parents='parent',
                    values='InvAmount',
                    )
    return f


# app.css.append_css({
#     'external_url': 'https://codepen.io/chriddyp/pen/bWLwgP.css'
# })

if __name__ == '__main__':
    app.run_server()
    # app.run_server(debug=True)
