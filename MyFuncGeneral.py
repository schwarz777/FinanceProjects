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
        return pxs.last('1D')
    except:
        print("unable loading", ticker, "from ", from_d, "to ", to_d)

    # example:
    # ticker = 'URW.AS'
    # get_last_close('URW.AS')


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
    assert (type(date) == dt.datetime)
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
import datetime as d
def get_tickers_history(tick_list:list, start, end = d.date.today() , this_price = 'Close', normalize_by=False):
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
    #get_tickers_history(tick_list= ['ABBN.SW', 'THBEV.SI', 'NSI.AS','KGX.DE','MSFT'],start="2017-01-05")


# example
# import datetime as dt
# tickers = ['ABBN.SW', 'PRX.AS', 'NSI.AS','KGX.DE','MSFT'] # add as many tickers
# start = dt.datetime(2017, 3,31)
# end = dt.datetime.today()
# tickhist = get_tickers_history(tickers,start, end, , 'Close')
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

import pandas as pd
def fill_up_series_with_closest(long_series:pd.Series, short_series:pd.DataFrame, closest_in='backward'):
    from datetime import datetime, timedelta
    assert(closest_in in ['backward' ,'forward','nearest'])
    if closest_in == 'past':
        long_series.sort_values(ascending = True)
        short_series.sort_index(ascending = True)
    else:
        long_series.sort_values(ascending=False)
        short_series.sort_index(ascending = False)

    #merge the dates that fit
    if closest_in == 'backward':
        short_series.index = short_series.index +  timedelta(days=1) #trick: just go one day forward with to_merge series to make comparison backward_or_equal!
    else:
        short_series.index = short_series.index - timedelta(days=1)  # trick: just go one day forward with to_merge series to make comparison backward_or_equal!
    merged_series = pd.merge_asof(long_series.to_frame(),short_series,left_index=True, right_index=True,direction=closest_in)
    return merged_series
    #long_series= pd.Series(range(20),index=pd.date_range('2018-09-01', periods=20, freq='m'),name='long')
    #short_series =pd.Series(range(1,5),index=pd.date_range('2017-01-01',periods=4,freq='y'),name='short')
    #fill_up_series_with_closest(long_series,short_series.to_frame())