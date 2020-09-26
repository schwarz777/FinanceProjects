# -*- coding: utf-8 -*-
"""
Created on Sun Jun 16 13:23:53 2019

@author: MichaelSchwarz
"""


# packages
# pip install yahoo-finance
# pip install yfinance
# pip install pandas-datareader
# pip matplotlib
# pip install cvxpy
# pip install plotly.express
# pip install mysql.connector
# pip install pandas_datareader
# import yfinance as yf

def get_last_close(ticker, pricesource='yahoo'):
    import pandas as pd
    import pandas_datareader.data as pdr
    import datetime as d
    import sys
    to_d = d.date.today()
    from_d = to_d - d.timedelta(days=10)
    try:
        px = pdr.DataReader(ticker, 'yahoo', from_d, to_d)
        pxs = pd.to_numeric(px.loc[:, "Adj Close"])
        return pxs[len(pxs) - 1]
    except:
        print("unable loading", ticker, "from ", from_d, "to ", to_d)

    # example: get_last_close('URW.AS')


# db connection
def cnx_mysqldb(database='fuyu'):
    """creates a connection to the local mysql-db for the specified database """
    import mysql.connector
    cnx = mysql.connector.connect(user='root', password='mysql4michi',
                                  host='127.0.0.1',
                                  database=database)
    return cnx
# df = pd.read_sql(query, con=cnx)
# import pandas as pd
# f


def date2mysqldatestring(date):
    import datetime as dt
    assert(type(date) == dt.datetime)
    return str(date)[0:10]


##example to call mysql procedure
# connection = mysql.connector.connect(host='localhost',
#                                         database='fuyu',
#                                         user='root',
#                                         password='mysql4michi')
# cursor = connection.cursor()
#
# cursor.callproc('usp_vpy_FilterMembercountForCluster', ['GICS'])
# results = [r.fetchall() for r in cursor.stored_results()]
# dfres = pd.DataFrame(results[0], columns = ['parent','child','members'])

# get prices
def get_tickers_history(start, end, tick_list, this_price, normalize_by=False):
    """ arg: `this_price` can take str Open, High, Low, Close, Volume
        arg: 'normalize_by' can take :
                    str 'shortest' to normalize all series by time series that has the latest new price
                    str 'first_price' to normalize each series by its first price
                    False for not normalizing
    """
    import pandas as pd
    import pandas_datareader.data as pdr
    # make an empty dataframe in which we will append columns
    dat = pd.DataFrame([])
    first_datapoint = list()
    # loop here to fetch all price data
    for idx, i in enumerate(tick_list):
        try:
            fetch_new = pdr.DataReader(i, 'yahoo', start, end)
            new = fetch_new[this_price]
            new.name = i
            first_datapoint.append(new.first_valid_index())
            dat = dat.merge(new, how='outer', left_index=True, right_index=True)
        except:
            print("No yahoo-data loaded for ticker", i)
    if normalize_by == 'shortest':
        # time series are normalized with the oldest price tick of the shortest  series
        dat = dat / dat.loc[max(first_datapoint)]
        print("All time series were normalized by: ", max(first_datapoint))
    elif normalize_by == 'first_price':
        # time series are normalized with the oldest price tick of each series
        dat = dat / dat.min()
    elif not normalize_by:
        print("the effective prices are returned")
    else:
        print("Your input for normalize_by" '', normalize_by, "' is not defined")
        exit(0)
    return dat
    # example
    # get_tickers_history(start="2017-01-05",end="2020-01-05",tick_list= ['ABBN.SW', 'THBEV.SI', 'NSI.AS','KGX.DE','MSFT'],this_price='Close',normalize_by = 'first_price').plot()


# example
# import datetime as dt
# tickers = ['ABBN.SW', 'PRX.AS', 'NSI.AS','KGX.DE','MSFT'] # add as many tickers
# start = dt.datetime(2017, 3,31)
# end = dt.datetime.today()
# tickhist = get_tickers_history(start, end, tickers, 'Close')
# tickhist.plot()

def col(df):
    return list(df.columns.values)


def get_source(func):
    import inspect
    lines = inspect.getsource(func)
    print(lines)

# STUFF###########
####alternative zu pandas....###
# def query_mysqldb(query, database='fuyu'):
#     try:
#         cnx = cnx_mysqldb(database)
#         cursor = cnx.cursor()
#         cursor.execute(query)
#         row = cursor.fetchone()
#         while row is not None:
#             print(row)
#             row = cursor.fetchone()
#     except Error as e:
#         print(e)
#     finally:
#         cursor.close()
#         cnx.close()
# query_mysqldb("select * from issue")
####end....######
def check_numeric(x):
    if not any([isinstance(x, int),
                isinstance(x, float),
           #     isinstance(x, long),
                isinstance(x, complex)]):
        raise ValueError('{0} is not numeric'.format(x))