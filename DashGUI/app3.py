# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import sys

sys.path.append(r'C:\Users\MichaelSchwarz\PycharmProjects\FinanceProjects')
import MyFuncGeneral as my

sys.path.append(r'C:/Users/MichaelSchwarz/PycharmProjects/FinanceProjects/PortfolioConstruction')
import evaluate_portfolio_exposure as epe

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

colors = {
    'background': '#111111',
    'text': '#7FDBFF'
}

# get the different Clusternames as Options for the Dropdown Choice for SunburstCluster Center
cnx = my.cnx_mysqldb('fuyu')
query = "select distinct NameMotherCluster from ( " + \
        "select level1 as NameMotherCluster from exposure_clusters_by_level " + \
        "union select '__________LEVEL2_________' union select distinct level2 from exposure_clusters_by_level )s"

dropdownLabClusters = pd.read_sql(query, con=cnx)

app.layout = html.Div([
    html.Div([
        html.Div([
            html.H3('BM-View'),

            dcc.Dropdown(
                id='NameMotherCluster',
                options=[dict(label=i, value=i) for i in dropdownLabClusters["NameMotherCluster"]],
                value="GICS"),
        ],
            style={'width': '25%',
                   'display': 'inline-block'}),

        dcc.Graph(id='funnel-graph',
                  figure=epe.evaluate_clusters_in_sunburst(most_inner_cluster='NameMotherCluster')
                  )
    ], className="six columns"
    ),

    html.Div([
        html.H3('Selected Companies View'),
        dcc.Graph(id='g2',
                  figure=epe.evaluate_portfolio_exposure(FilterCompanies="all", CategoryType="GICS",
                                                         DrilldownLevel=1))
    ], className="six columns"),
], className="row")


@app.callback(
    dash.dependencies.Output('funnel-graph', 'figure'),
    [dash.dependencies.Input('NameMotherCluster', 'value')])
def update_graph(cat_type):
    epe.evaluate_clusters_in_sunburst(most_inner_cluster=cat_type)


app.css.append_css({
    'external_url': 'https://codepen.io/chriddyp/pen/bWLwgP.css'
})

# figure = epe.evaluate_clusters_in_sunburst(
#    most_inner_cluster='GICS')  # epe.evaluate_portfolio_exposure(FilterCompanies="all", CategoryType="MSSC",DrilldownLevel=4)

if __name__ == '__main__':
    app.run_server(debug=True)
