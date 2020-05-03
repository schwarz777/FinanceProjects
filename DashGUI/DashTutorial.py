import dash
import dash_core_components as dcc
import dash_html_components as html
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

df = pd.read_csv(
    'https://gist.githubusercontent.com/chriddyp/' +
    '5d1ea79569ed194d432e56108a04d188/raw/' +
    'a9f9e8076b837d541398e999dcbac2b2826a81f8/' +
    'gdp-life-exp-2007.csv')

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
                          dcc.Markdown(children=markdown_text),
                          dcc.Dropdown(
                              options=optionsmenu_own,
                              value='GICS'
                          ),
                          html.Label('Please enter your comment!'),
                          dcc.Input(value='MTL', type='text'),

                          dcc.Graph(
                              id='life-exp-vs-gdp',
                              figure=epe.evaluate_clusters_in_sunburst(most_inner_cluster='GICS')

                          )
]
)


if __name__ == '__main__':
    app.run_server(debug=True)
