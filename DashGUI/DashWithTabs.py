import dash
import dash_html_components as html
import dash_core_components as dcc
import sys

# from StockSelection.CompanyClass import Company

sys.path.append(r'C:\Users\MichaelSchwarz\PycharmProjects\FinanceProjects')
import MyFuncGeneral as my

sys.path.append(r'C:/Users/MichaelSchwarz/PycharmProjects/FinanceProjects/PortfolioConstruction')
import evaluate_portfolio_exposure as epe

from dash.dependencies import Input, Output

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

# get company info
sys.path.append(r'C:/Users/MichaelSchwarz/PycharmProjects/FinanceProjects/StockSelection')
import CompanyClass as c
c1 = c.Company("PRX.AS")
c2 = c.Company("EVD.DE")
fig_prep = c1.compare(start="2020-01-05", end="2020-05-25")

# Company.compare(c1, start="2015-01-05", end="2020-05-25")

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
        return html.Div([
            html.H3('Stocks Relative'),
            dcc.Graph(id='stocks_rel', figure=fig_prep)
        ])
    elif tab == 'tab-2':
        return html.Div([
            html.H3('Relative Development over time'),
            dcc.Graph(id='portfolio_view', figure=epe.evaluate_clusters_in_sunburst(most_inner_cluster='GICS'))
        ])


if __name__ == '__main__':
    app.run_server(debug=True)
