# -*- coding: utf-8 -*-
"""
Created on Sun Jan  5 18:07:08 2020

@author: MichaelSchwarz

Evaluate a portfolio's exposure after different categorizations


"""


def evaluate_portfolio_exposure(FilterCompanies="all", CategoryType="GICS", DrilldownLevel=1):
    """gets the chosen companies with its categorisations from mySQL, adds prices and pie-charts it 
    
    In:
    FilterCompanies -- Filter only for Companies in a certain group like CurrentPortfolio,...
    CategoryType    -- The main category for categorization
    DrilldownLevel  -- Granularity at which the categorization is displayed 1:5 
    
    """
    import sys
    sys.path.append(r'C:\Users\MichaelSchwarz\PycharmProjects\FinanceProjects')
    import MyFuncGeneral as My

    # checks
    assert FilterCompanies in str(["all", "CurrentPortfolio"])
    assert CategoryType in str(["GICS", "MSHN", "MSRC", "MSSC"])
    assert DrilldownLevel in range(1, 6)
    cnx = My.cnx_mysqldb('fuyu')
    if FilterCompanies != "CurrentPortfolio":

        query = "select * from vcurrentportfolio p " + \
                "inner join vexposurevalues_per_parent_cluster_and_issuer e on p.IssueID=e.IssuerID " + \
                "where e.ParentClusterlevel=1 and p.unitsOwned<>0"
    else:
        query = "select * from vcurrentportfolio p " + \
                "inner join vexposurevalues_per_parent_cluster_and_issuer e on p.IssueID=e.IssuerID " + \
                "where e.ParentClusterlevel=1 and p.unitsOwned<>0"

    import pandas as pd
    comp_with_cat = pd.read_sql(query, con=cnx)
    comp_with_cat['last_price'] = pd.Series(None, index=comp_with_cat.index)

    # get last closing prices
    for i in range(0, len(comp_with_cat)):
        px = My.get_last_close(comp_with_cat.loc[i, 'Ticker_yahoo'])
        comp_with_cat.loc[i, 'last_price'] = px

    comp_with_cat['InvAmount'] = comp_with_cat.last_price * comp_with_cat.UnitsOwned

    # plot
    import plotly.express as px
    fig = px.pie(comp_with_cat, values='InvAmount', names='Ticker_yahoo', title='My current Portfolio')
    import plotly.io as pio
    # pio.renderers
    pio.renderers.default = 'svg'  # usingorca... -> static file
    return fig
    # fig.write_html('first_figure.html', auto_open=True)


#  return(comp_with_cat)


# example
# FilterCompanies="all"; CategoryType="GICS";DrilldownLevel=1
# d=evaluate_portfolio_exposure(FilterCompanies="all", CategoryType="MSSC",DrilldownLevel=4)

# sunburst Chart
def evaluate_clusters_in_sunburst(most_inner_cluster):
    import pandas as pd
    import plotly.express as px
    import sys
    sys.path.append('C:/Users/MichaelSchwarz/.spyder-py3/myPyCode')
    import mysql.connector

    connection = mysql.connector.connect(host='localhost',
                                         database='fuyu',
                                         user='root',
                                         password='mysql4michi')
    cursor = connection.cursor()

    cursor.callproc('usp_vpy_FilterMembercountForCluster', [most_inner_cluster])
    results = [r.fetchall() for r in cursor.stored_results()]
    dfres = pd.DataFrame(results[0], columns=['parent', 'child', 'members'])
    dfres.to_dict()

    # fig = px.sunburst(
    #     dfres,
    #     names='child',
    #     parents='parent',
    #     values='members',
    # )
    return dfres


if __name__ == '__main__':
    f = evaluate_clusters_in_sunburst(most_inner_cluster='MSHN')
    f.show()
