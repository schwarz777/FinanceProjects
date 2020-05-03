# -*- coding: utf-8 -*-
import sys

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
query = "select distinct level1 as NameMotherCluster from exposure_clusters_by_level " + \
        "union select '__________LEVEL2_________' " + \
        "union select distinct level2 from exposure_clusters_by_level"

dropdownLabClusters = pd.read_sql(query, con=cnx)
dropdownLabClusters_obj = [{
    'label': i,
    'value': i
} for i in dropdownLabClusters["NameMotherCluster"]]

app.layout = html.Div([
    html.Div([
        html.Div([
            html.H3('BM-View'),

            dcc.Dropdown(
                id='NameMotherCluster',
                options=dropdownLabClusters_obj,
                placeholder="Select Business Area",
                style=dict(
                    width='40%',
                    display='inline-block',
                    verticalAlign="middle"
                )
            ),

            dcc.Graph(id='NameMotherCluster',
                      figure=epe.evaluate_clusters_in_sunburst(most_inner_cluster='GICS')
                      # epe.evaluate_portfolio_exposure(FilterCompanies="all", CategoryType="MSSC",DrilldownLevel=4)
                      )
        ], className="six columns"),

        html.Div([
            html.H3('Selected Companies View'),
            dcc.Graph(id='g2',
                      figure=epe.evaluate_portfolio_exposure(FilterCompanies="all", CategoryType="GICS",
                                                             DrilldownLevel=1))
        ], className="six columns"),
    ], className="row")
])

app.css.append_css({
    'external_url': 'https://codepen.io/chriddyp/pen/bWLwgP.css'
})

figure = epe.evaluate_clusters_in_sunburst(
    most_inner_cluster='GICS')  # epe.evaluate_portfolio_exposure(FilterCompanies="all", CategoryType="MSSC",DrilldownLevel=4)

if __name__ == '__main__':
    app.run_server(debug=True)
