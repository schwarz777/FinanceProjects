import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.graph_objs as go
import sys

# own functions
sys.path.append(r'C:\Users\MichaelSchwarz\PycharmProjects\FinanceProjects')
import MyFuncGeneral as my

sys.path.append(r'C:/Users/MichaelSchwarz/PycharmProjects/FinanceProjects/PortfolioConstruction')
import evaluate_portfolio_exposure as epe

app = dash.Dash()

colors = {
    'background': '#111111',
    'text': '#7FDBFF'
}

markdown_text = '''
###world is beautiful \n
and I want to see it!
'''

# dropdown
# get the different Clusternames as Options for the Dropdown Choice for SunburstCluster Center
cnx = my.cnx_mysqldb('fuyu')
query = "select distinct NameMotherCluster from ( " + \
        "select level1 as NameMotherCluster from exposure_clusters_by_level " + \
        "union select '__________LEVEL2_________' union select distinct level2 from exposure_clusters_by_level )s " + \
        "where NameMotherCluster is not null "

dropdownLabClusters = pd.read_sql(query, con=cnx)
optionsmenu_own = [dict(label=i, value=i) for i in dropdownLabClusters["NameMotherCluster"]]

app.layout = html.Div([
    html.Div([
        html.Div([
            html.H3("Cluster Split"),
            dcc.Markdown(children=markdown_text),
            dcc.Dropdown(
                id='dropdown-id',
                options=optionsmenu_own,
                value='GICS'
            ),
            html.Label('Please enter your comment!'),
            dcc.Input(value='cheap shares are great!', type='text'),
            dcc.Graph(id='sunburst-graph')

        ], className="six columns"),
        html.Div([
            html.H3('Selected Companies View'),
            dcc.Graph(id='g2',
                      figure=epe.evaluate_portfolio_exposure(FilterCompanies="all", CategoryType="GICS",
                                                             DrilldownLevel=1))
        ], className="two columns"),
    ], className="row")
])


@app.callback(
    dash.dependencies.Output('sunburst-graph', 'figure'),
    [dash.dependencies.Input('dropdown-id', 'value')]
)
def update_output_div(input_value):
    f = epe.evaluate_clusters_in_sunburst(most_inner_cluster=input_value)
    return f

app.css.append_css({
    'external_url': 'https://codepen.io/chriddyp/pen/bWLwgP.css'
})

if __name__ == '__main__':
    app.run_server(debug=True)
