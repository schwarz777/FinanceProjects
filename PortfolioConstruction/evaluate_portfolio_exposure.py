# -*- coding: utf-8 -*-
"""
Created on Sun Jan  5 18:07:08 2020

@author: MichaelSchwarz

Evaluate a portfolio's exposure after different categorizations


"""
def evaluate_portfolio_exposure(put_currentprrices_in_db=False):
    """gets the chosen current portfolio from mySQL, adds prices and pie-charts it ()

    In:
    put_currentprices_in_db -- if True: write back loaded current prices into mysql

    """
    import sys
    sys.path.append(r'C:/Users/MichaelSchwarz/PycharmProjects/FinanceProjects')
    import MyFuncGeneral as My
    cnx = My.cnx_mysqldb('fuyu')
    query = "select * from vcurrentportfolio p where UnitsOwned <>0"


    import pandas as pd
    comps = pd.read_sql(query, con=cnx)
    comps['last_price'] = pd.Series(None, index=comps.index)

    # get last closing prices
    for i in range(0, (len(comps))):
        try:
            px = My.get_last_close(comps.loc[i, 'Ticker_yahoo'])
            comps.loc[i, 'last_price'] = px.values
        except:
            print("for company no price could be loaded")
    if put_currentprrices_in_db:
        import datetime as dt
        prices_current_portfolio = comps[['IssueID','last_price']] # 'yahoo', ,dt.date.today())
        prices_current_portfolio.columns = ['FK_IssueID', 'Price']
        prices_current_portfolio['FK_Datasource'] = 'yahoo'
        prices_current_portfolio['PriceDate'] = dt.date.today()
        cnx = My.cnx_mysqldb('fuyu_jibengong')
        cursor=cnx.cursor()
        #delete current entries
        table = 'fuyu_jibengong.portfolio_issue_prices_current'
        query_del =  "delete from " + table
        cursor.execute(query_del)
        #add current tickers with prices
        add_prices = ("INSERT INTO  " + table +
                      "(FK_IssueID, Price, FK_Datasource, PriceDate) "
                      "VALUES (%s, %s, %s, %s)")
        p_list = prices_current_portfolio.values.tolist()
        cursor.executemany(add_prices,p_list)
        cnx.commit()
        print(cursor.rowcount, "prices were inserted.")

    cursor.close()
    cnx.close()


    comps['InvAmount'] = comps.last_price * comps.UnitsOwned

    # plot
    import plotly.express as px
    fig = px.pie(comps, values='InvAmount', names='Ticker_yahoo', title='My current Portfolio')
    import plotly.io as pio
    # pio.renderers
    pio.renderers.default = 'svg'  # usingorca... -> static file
    return fig


# example
# fig=evaluate_portfolio_exposure(put_currentprices_in_db = True)
# fig.write_html('first_figure.html', auto_open=True)

# sunburst Chart
def cluster_data_for_sunburst_eval(most_inner_cluster):
    import pandas as pd
    import sys
    sys.path.append('C:/Users/MichaelSchwarz/.spyder-py3/myPyCode')
    import mysql.connector

    fig_portfolio = evaluate_portfolio_exposure(put_currentprrices_in_db=True) #gets portfolio data AND writes current prices in DB!!!

    #todo replace with function My.cnx_mysqldb(database='fuyu'):
    connection = mysql.connector.connect(host='localhost',
                                         database='fuyu',
                                         user='root',
                                         password='mysql4michi')
    cursor = connection.cursor()
    #Todo  check input parameter most_inner_cluster
    # get allowed
    #assert FilterCompanies in str(["all", "CurrentPortfolio"])

    # get current portfolio

    #find prices and write into sql

    #get portfolio clustered
    
    #plot
    #cursor.callproc('usp_vpy_FilterMembercountForCluster', [most_inner_cluster])
    cursor.callproc('usp_vpy_ScreenPortfolioByCluster', [most_inner_cluster])
    results = [r.fetchall() for r in cursor.stored_results()]
    dfres = pd.DataFrame(results[0], columns=['parent', 'child', 'InvAmount'])
    dfres.to_dict()

    return dfres


if __name__ == '__main__':
    dfres = cluster_data_for_sunburst_eval(most_inner_cluster='GICS')
    import plotly.express as px

    fig = px.sunburst(
        dfres,
        names='child',
        parents='parent',
        values='InvAmount',
    )
    fig.write_html('first_figure.html', auto_open=True)