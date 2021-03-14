import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys
import datetime as dt
import xarray as xr
import matplotlib.pyplot as plt
import plotly
from plotly.tools import mpl_to_plotly
#import matplotlib.pyplot as plt

sys.path.append(r'C:\Users\MichaelSchwarz\PycharmProjects\FinanceProjects')
import MyFuncGeneral as my

# PREPARE TAB1 STOCKS RELATIVE
sys.path.append(r'C:/Users/MichaelSchwarz/PycharmProjects/FinanceProjects/StockSelection')
import CompanyClass as c

# get the tickers to display
def create_companies():
    cnx = my.cnx_mysqldb('fuyu')
    query = "select * from issues_yh_now_selected"
    comps = pd.read_sql(query, con=cnx)
    c.Company.remove_all_companies()  # remove all companies before new ones are created!
    if len(comps) == 0 or len(comps) > 20:
        print("none or too many (>20) companies selected to display - correct in livecode")
    else:
        for i in comps['Ticker_yahoo']:
            try:
                cobj = c.Company(i)
            except:
                print("For selected Company "+i+" the Company-Object could not be generated")
    cnx.close()
    return  cobj # example dat
    # arb_company=create_companies()


default_start = dt.date.today() - dt.timedelta(days= 20 * 365)
default_end = dt.date.today()
datrange = pd.date_range(default_start,default_end)
numdate = [x for x in range(len(datrange))]
arb_comp = create_companies()

# DEFINE DROPDOWN MENUS
# kf selection for rel. valuation
all_kf = ['AssetBase', 'Operating Earnings',  'NetIncome', 'operating CF',
          'Operating Earnings incl non-core', 'Operating Earnings after capex',
          'Operating Earnings Equ', 'Operating Earnings Equ incl non-core', 'Operating Earnings after capex Equ',
         'operating CF after capex']

optionsmenu_kf = [dict(label=i, value=i) for i in all_kf]
chosen_kfs = all_kf[0:4]
hist_kf = all_kf[0]

# display as
display_vls = ['YtFV' , 'Premium/discount', 'Multiple','Other']
optionsmenu_display_as = [dict(label=i, value=i) for i in display_vls]

# cluster
cnx = my.cnx_mysqldb('fuyu')
query = "select * from vlc_all_exposure_clusters_with_id where left(CatNameInTree,4) not in ('MSSC','MSRC')"
available_clusters = pd.read_sql(query, con=cnx)
cnx.close
optionsmenu_companies_of_cluster=[]
for i in range(len(available_clusters)):
    optionsmenu_companies_of_cluster.append(dict(label=available_clusters.loc[i,"CatNameInTree"],
                                    value =available_clusters.loc[i,"ID"] )
                               )



# PREPARE TAB3 PORTFOLIO
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
cnx.close()
optionsmenu_cluster = [dict(label=i, value=i) for i in dropdownLabClusters["NameMotherCluster"]]

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
# APP START
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div([

    dcc.Tabs(id='tabs-example', value='tab-1', children=[
        dcc.Tab(label='Stocks Relative Performances', value='tab-1'),
        dcc.Tab(label='Stocks Relative Valuations', value='tab-2'),
        dcc.Tab(label='Portfolio', value='tab-3'),
    ]),
    html.Div(id='tabs-example-content')
])


@app.callback(Output('tabs-example-content', 'children'),
              [Input('tabs-example', 'value')])
def render_content(tab):
    if tab == 'tab-1':
        fig = arb_comp.compare(start=default_start, end=default_end)
        return html.Div([
            dcc.Markdown('''
            #### Stock Performance normalized by start date
            if a stock with shorter history is chosen, normalized as of shortest
            '''),
            dcc.Graph(id='stocks_rel', figure=fig),
            dcc.RangeSlider(
                    id='my-range-slider',
                      max=  numdate[-1]
                  ,marks =   {0:datrange[0].date() ,
                             int(len(datrange)/6): datrange[int(len(datrange)/6)].date(),
                             int(len(datrange) *2/ 6): datrange[int(len(datrange)*2 / 6)].date(),
                             int(len(datrange) * 3 / 6): datrange[int(len(datrange) * 3 / 6)].date(),
                             int(len(datrange) *4/ 6): datrange[int(len(datrange)*4 / 6)].date(),
                             int(len(datrange) * 5/ 6): datrange[int(len(datrange) * 5 / 6)].date(),
                             len(datrange): datrange[len(datrange)-1]}
                    ,value=[int(len(datrange) * 5 / 6), numdate[-1]]
                )

        ])
    elif tab == 'tab-2':
        return html.Div([
            dcc.Dropdown(
                id='clusterdropdown-id',
                options=optionsmenu_companies_of_cluster,
                value='none'
            ),
            # dcc.Dropdown(
            #     id='ShowValuationAs-id',
            #     options=optionsmenu_display_as,
            #     value='YtFV'
            # ),
            html.Div([
                html.Div([
                    html.H6('One Keyfigure Historic'),
                    dcc.Dropdown(
                        id='kfdropdown-id',
                        options=optionsmenu_kf,
                        value=hist_kf
                    ),
                    dcc.Graph(id='graph-valuation-view-hist')
                ], className="six columns"),

                html.Div([
                    html.H6('Various Keyfigures Live'),
                    dcc.Dropdown(
                        id='spiderdropdown-id',
                        options=optionsmenu_kf,
                        value=chosen_kfs,
                        multi=True
                    ),
                    dcc.Graph(id='graph-valuation-view-spider')
                ], className="six columns"),
            ], className="row")

       ,
        ])
    elif tab == 'tab-3':
        return html.Div([
            html.H3('Composition by different Clusters'),
            dcc.Dropdown(
                id='dropdown-id',
                options=optionsmenu_cluster,
                value='GICS'
            ),
            # dcc.Textarea(id='text', value="test"),
            dcc.Graph(id='graph-portfolio-view')
        ])

#tab1
@app.callback(
    dash.dependencies.Output('stocks_rel', 'figure'),
    [dash.dependencies.Input('my-range-slider', 'value')])
def update_output(value):
   new_start = datrange[value[0]]
   new_end = datrange[value[1]]
   fig = arb_comp.compare(start=new_start, end=new_end)
   return fig#'You have selected '+ str(new_start) + 'to' + str(new_end)

#tab2 - cluster function
# def update_select_company_by_cluster(clusterdropdown_id):
#     if any(cluster_id):
#         query = "insert into issues_yh_now_selected" + \
#                 "selectTicker_yahoo,c.Issue_name" + \
#                 "from Issue i inner join" + \
#                 "vlc_show_exposure_clusters_per_company c on " + \
#                 "i.issue_Name=c.Issue_name and c.allCat="+str(cluster_id)+ \
#                 " Limit 20"
#         cnx = my.cnx_mysqldb('fuyu')
#         cur = cnx.cursor()
#         try:
#             cur.execute(query)
#             cnx.commit()
#         except Exception as e:
#             print("insert selected ticker's members did not work")
#             print(e)
#             cnx.rollback()
#         cnx.close()

#tab2 -
@app.callback(
    dash.dependencies.Output('graph-valuation-view-hist', 'figure'),
    [dash.dependencies.Input('kfdropdown-id', 'value')]
)
#tab2 - hist
def update_val_output_div(chosen_kf):#,cluster_id):
   # update_select_company_by_cluster(cluster_id)
    val = arb_comp.get_vals([chosen_kf])[:, 0, :].to_pandas()
    df = val.melt(ignore_index=False)
    fig_histval = px.line(df, x=df.index, y="value", color="company", labels={"value": "YtFV", "variable": "company",
                                                                              'x': "hist reporting period (and price) to calc KF"})
    return fig_histval

#tab2 - spider
@app.callback(
    dash.dependencies.Output('graph-valuation-view-spider', 'figure'),
    [dash.dependencies.Input('spiderdropdown-id', 'value')]
)
def update_val_output_div(chosen_kf):
    if isinstance(chosen_kf, str):
        chosen_kf = [chosen_kf]
    VAL = arb_comp.get_vals(chosen_kf,keyinputset='Default', displayMethod='YtFV', WACC=None)
    df = VAL.sel(period=max(VAL._getitem_coord("period"))).to_pandas()
    df = df.melt(ignore_index=False)
    fig_spider = px.line_polar(df, r="value", theta=df.index, color="company", line_close=True,
                        color_discrete_sequence=px.colors.sequential.Plasma_r)
    return fig_spider

#tab3
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


app.css.append_css({
    'external_url': 'https://codepen.io/chriddyp/pen/bWLwgP.css'
})

if __name__ == '__main__':

    app.run_server()
    # app.run_server(debug=True)
