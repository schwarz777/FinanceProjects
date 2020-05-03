# -*- coding: utf-8 -*-
"""
Created on Sun Jun 16 13:23:53 2019

@author: MichaelSchwarz
"""
#functions
def cnx_mysqldb(database='fuyu'):
    """creates a connection to the local mysql-db for the specified database """
    import mysql.connector as mscn
    cnx = mscn.connect(user='root', password='mysql4michi',
                              host='127.0.0.1',
                              database=database)
    return cnx


#get optimization inputs
import pandas as pd
#create data frame to fill in opt-inputs
d = {'YahooTicker':[],'lb':[],'ub':[],'signal':[]}
opt_in = pd.DataFrame(data=d)
query = "select Ticker_yahoo from vlast_trade_evals where Action='OWN'"
cnx=cnx_mysqldb()
tickers = pd.read_sql(query, con=cnx)
tickers = tickers['Ticker_yahoo']
#fill in optimization input df
#get mysql inputs (ticker list)   
opt_in['YahooTicker'] = tickers
opt_in['lb'] = 0
opt_in['ub'] = 1
opt_in['signal'] =1/opt_in.shape[0]



#get the prices to calculate covariance
#from pandas_datareader import data
#import matplotlib.pyplot as plt
import pandas_datareader.data as pdr
tick = opt_in['YahooTicker']
#import yfinance as yf
import datetime as dt
#start=dt.datetime.strptime("2019-01-01",'%Y-%m-%d') 
#end=dt.datetime.strptime("2019-04-30",'%Y-%m-%d') 
start="2019-01-05" 
end="2019-08-30" 
panel_data = pdr.DataReader(tick, 'yahoo', start, end)

adj_close=panel_data['Adj Close']
all_weekdays = pd.date_range(start=start, end=end, freq='B')
adj_close = adj_close.reindex(all_weekdays)  
adj_close_norm=adj_close.divide(adj_close.iloc[2]/100)
adj_close_norm.plot()
#calculate covariance matrix
r=adj_close/adj_close.shift(1)-1
r.plot()
COV=r.cov()

import matplotlib.pyplot as plt
plt.matshow(COV)
plt.show()
plt.matshow(r.corr())


#optimize
#pip install nlopt 
# https://nlopt.readthedocs.io/en/latest/NLopt_Python_Reference/#using-the-nlopt-python-api
import numpy 
import nlopt
from numpy import *

n = len(opt_in)
opt = nlopt.opt(nlopt.GN_ISRES,n)

def f(x,grad):
    if grad.size > 0:
        grad=numpy.ones(len(x))*2
    return(sum(x**2))
opt.set_min_objective(f)
    
def h(x,grad): 
    if grad.size > 0:
        grad=numpy.ones(len(x))
    return(sum(x)-1) 
opt.add_equality_constraint(h)

opt.set_lower_bounds(opt_in.loc[:,'lb'])
opt.set_upper_bounds(opt_in.loc[:,'ub'])

rb=opt_in.loc[:,'signal']
x0=numpy.ones(n)
OptRes = opt.optimize(x0)


#optimize2 using cvxpy
import cvxpy


#display results


