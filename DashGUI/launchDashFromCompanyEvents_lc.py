# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html

import sys
sys.path.append(r'C:/Users/MichaelSchwarz/PycharmProjects/FinanceProjects/PortfolioConstruction')
import evaluate_portfolio_exposure as epe

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

colors = {
    'background': '#111111',
    'text': '#7FDBFF'
}

app.layout = html.Div([
    html.Div([
        html.Div([
            html.H3('BM-View'),
            dcc.Graph(id='g1',
                      figure=epe.cluster_data_for_sunburst_eval(most_inner_cluster='GICS')
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

figure = epe.cluster_data_for_sunburst_eval(
    most_inner_cluster='')  # epe.evaluate_portfolio_exposure(FilterCompanies="all", CategoryType="MSSC",DrilldownLevel=4)

if __name__ == '__main__':
    app.run_server(debug=True)
