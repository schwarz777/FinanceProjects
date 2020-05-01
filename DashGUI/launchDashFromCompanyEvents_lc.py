# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd

exec(open("C:/Users/MichaelSchwarz/.spyder-py3/myPyCode/evaluate_portfolio_exposure.py").read())
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
                      figure=epe.evaluate_clusters_in_sunburst(MostInnerCluster='GICS') #epe.evaluate_portfolio_exposure(FilterCompanies="all", CategoryType="MSSC",DrilldownLevel=4)
)
        ], className="six columns"),

        html.Div([
            html.H3('Selected Companies View'),
            dcc.Graph(id='g2', 
                      figure=epe.evaluate_portfolio_exposure(FilterCompanies="all", CategoryType="GICS",DrilldownLevel=1))
        ], className="six columns"),
    ], className="row")
])

app.css.append_css({
    'external_url': 'https://codepen.io/chriddyp/pen/bWLwgP.css'
})



figure=epe.evaluate_clusters_in_sunburst(MostInnerCluster='') #epe.evaluate_portfolio_exposure(FilterCompanies="all", CategoryType="MSSC",DrilldownLevel=4)

if __name__ == '__main__':
    app.run_server(debug=True)
    
    
   