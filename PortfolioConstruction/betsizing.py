# -*- coding: utf-8 -*-
"""
Created on Sun Jun 16 13:23:53 2019

@author: MichaelSchwarz
"""

# get optimization inputs
import pandas as pd
import numpy as np
import sys
import datetime as dt
import scipy.optimize
import pandas_datareader.data as pdr

sys.path.append(r'C:\Users\MichaelSchwarz\PycharmProjects\FinanceProjects')
import MyFuncGeneral as My
import matplotlib.pyplot as plt


def get_cov(start,end,tick,plot_cov=False):
    """calc covariance matrix for companies in tick, prices from yahoo between start and end.
    na-observations are just ignored"""
    panel_data = pdr.DataReader(tick, 'yahoo', start, end)

    adj_close = panel_data['Adj Close']
    all_weekdays = pd.date_range(start=start, end=end, freq='B')
    adj_close = adj_close.reindex(all_weekdays)
    adj_close_norm = adj_close.divide(adj_close.iloc[2] / 100)

    # calculate covariance matrix
    r = adj_close / adj_close.shift(1) - 1

    COV = r.cov()

    if plot_cov:
        adj_close_norm.plot()
        r.plot()
        plt.matshow(COV)
        plt.show()
        plt.matshow(r.corr())
    return COV

# do the Risk Contribution Optimization RCO
def rco(signals,cov,bounds=None,te_targ=None):
    dir = np.where(signals>=0,1,-1)
    rb = abs(signals) / sum(abs(signals))
    w0 = rb *dir

    if bounds is not None :
        bnds = scipy.optimize.Bounds(bounds["lb"].values,bounds["ub"].values,keep_feasible = True)
    else:
        bnds =bounds

    from scipy.optimize import minimize #using scipy optimizer:
    if any(signals<0):
        # Approach Baltas 2013 p23 Long-short Extended Risk Parity
        ####target function
        #debug definitions: w=w0;signal=signals
        assert (te_targ is not None)
        def rco_targ_fun_long_short(w: np.array, signal: np.array, cov: pd.DataFrame, te_targ: float):
            res = - np.abs(signal) @ np.log(np.abs(w))  # same as sum(np.abs(signal) * np.log(np.abs(w))), -1 as unlike Baltas we need to have a Minimize function here!
            return res
        ####constraints (to be zero if equality-constraint and non-negative if unequality-constraint)
        def te_constraint(w: np.array, signal: np.array, cov: pd.DataFrame, te_targ: float):
            return te_targ ** 2 - w.T @ cov @ w
        def direction_constraint(w: np.array, signal: np.array, cov: pd.DataFrame, te_targ: float):
            A = np.diag(dir)
            return A.dot(w)
        def total_weight_constraint(w: np.array, signal: np.array, cov: pd.DataFrame, te_targ: float):
            # return np.sum(np.log(abs(x)))-1
            tol=0.05
            return [np.sum(w)*(1-tol),-(1-tol)*np.sum(w) ]

        arguments = (signals,cov,te_targ)
        cons = ({'type': 'ineq', 'fun': te_constraint,'args': arguments}
               , {'type': 'ineq', 'fun': direction_constraint,'args': arguments}
               , {'type': 'ineq', 'fun': total_weight_constraint, 'args': arguments}
                )
        res = minimize(rco_targ_fun_long_short,w0,args=arguments,
                       method='SLSQP', constraints=cons,
                       options={'disp': False, 'maxiter': 200},
                       bounds=bnds)

        ###TE-target met?
        te_error_margin = 0.0001
        te_opt = np.sqrt(res.x.T @ cov @ res.x)
        if abs(te_opt - te_targ) > te_error_margin:
            print("TE is " + str(round(te_opt, 7)) + " instead of TE-target " + str(te_targ))

    else:
        # Simple direct approach for Long-Only
        ####target function
        def rco_targ_fun_long_only(w: np.array, rb: np.array, cov: pd.DataFrame):
            """rb has same information as signal as direction is always positive"""
            var = w.T @ cov @ w
            delta = w * (cov @ w) / var - rb
            res = sum(delta * delta)
            return res

        ####constraints
        def total_weight_constraint(x):
            # return np.sum(np.log(abs(x)))-1
            return 1 - np.sum(x)

        def long_only_constraint(x):
            return x
        cons = (
                #{'type': 'ineq', 'fun': total_weight_constraint} ,
                 {'type': 'ineq', 'fun': long_only_constraint}
                )
        res = minimize(rco_targ_fun_long_only, w0, args=(rb, cov),
                       method='SLSQP', constraints =cons,
                       options={'disp':False,'maxiter':200},
                       bounds=bnds)
        res.x=res.x/sum(res.x)  #in long only case convenient scaling to 100% investment

    #checks
    ###direction correct?
    if any(res.x*dir < 0) is True:
        print("At least one direction constraint violated")

    ###investment
    print("Sum of all investments is: "+ str(round(sum(res.x),3)))

    return res

    #trial with cvxpy: problem non DCP-side constraint!?!
    # import cvxpy as cp
    # x = cp.Variable(len(w0))
    # cov = np.array(cov)
    # #objective = cp.Minimize(cp.sum_squares(x @ cov/ (x @ cov @ x)  -rb))
    # objective = cp.Maximize(sum(cp.log(x)))
    #     #sum((np.matmul(cov,x) / np.matmul(x.transpose(),np.matmul(cov,x)) -rb)**2))
    # #lb = np.zeros(len(ub))
    # constraints = [ lb <= x, x <= ub, x @ cov @ x <= te_targ**2 ]
    # prob = cp.Problem(objective,constraints )
    # prob.solve()
    # prob
    # print("Optimal value", prob.solve())
    # print("Optimal var")
    # print(x.value)  # A numpy ndarray.

def get_rc(w, cov):
    rc = (w * (cov @ w)) / (w.T @ cov @ w)
    return rc

def eval_rco(w,signals,cov,plot_it=True):
    rc=get_rc(w, cov)
    rb=abs(signals)/sum(abs(signals))
    dev_from_rb = sum(abs(rc-rb))
    if plot_it:
        import matplotlib.pyplot as plt
        colors = np.where(w>=0,"green","red")
        area = (200/max(w)) * abs(w)
        plt.scatter(rb,rc,color=colors,s=area)
        plt.xlabel("risk budget")
        plt.ylabel("risk contribution optimizied")
        plt.title("total deviation from risk budget is: " + str(round(dev_from_rb,2)) + " @TE: "+ str(round((w.T@cov@w)**0.5,3)*100) +"%")
    return dev_from_rb

if __name__ == '__main__':
    query = "select Ticker_yahoo from vcurrentportfolio where unitsowned>0"
    cnx = My.cnx_mysqldb()
    tick = pd.read_sql(query, con=cnx)['Ticker_yahoo']
    start = "2019-01-05"
    end = dt.date.today()
    cov = get_cov(start, end, tick, False)
    signals1 = np.ones(len(tick))
    signals2 = np.random.random(len(tick))
    signals3 = 2* (np.random.random(len(tick)) - 0.5)
    signals4 = signals3*np.where(np.random.random(len(tick))>0.5,1,-1)
    ub = np.ones(len(tick));lb =- ub #no restrictions to start
    bounds = pd.DataFrame(columns=['lb','ub'], index =tick)
    bounds["lb"]=lb;bounds["ub"]=ub
    signals=signals1
    te_targ = 0.02
    res = rco(signals,cov,bounds,te_targ)
    eval_rco(res.x,signals,cov,te_targ)

# OLD
# create data frame to fill in opt-inputs
# d = {'YahooTicker': [], 'lb': [], 'ub': [], 'signal': []}
# opt_in = pd.DataFrame(data=d)
# query = "select Ticker_yahoo from vcurrentportfolio"
# cnx = My.cnx_mysqldb()
# tickers = pd.read_sql(query, con=cnx)
# tickers = tickers['Ticker_yahoo']
# fill in optimization input df
# get mysql inputs (ticker list)
# opt_in['YahooTicker'] = tickers
# opt_in['lb'] = 0
# opt_in['ub'] = 1
# opt_in['signal'] = 1 / opt_in.shape[0]

# # optimize different way
# # pip install nlopt
# # https://nlopt.readthedocs.io/en/latest/NLopt_Python_Reference/#using-the-nlopt-python-api
# import numpy
# import nlopt
# from numpy import *
#
# n = len(opt_in)
# opt = nlopt.opt(nlopt.GN_ISRES, n)
#
# def f(x, grad):
#     if grad.size > 0:
#         grad = numpy.ones(len(x)) * 2
#     return (sum(x ** 2))
#
#
# opt.set_min_objective(f)
#
#
# def h(x, grad):
#     if grad.size > 0:
#         grad = numpy.ones(len(x))
#     return (sum(x) - 1)
#
#
# opt.add_equality_constraint(h)
#
# opt.set_lower_bounds(opt_in.loc[:, 'lb'])
# opt.set_upper_bounds(opt_in.loc[:, 'ub'])
#
# rb = opt_in.loc[:, 'signal']
# x0 = numpy.ones(n)
# OptRes = opt.optimize(x0)
# print(OptRes)
# #mv optimization
# import PyPortfolioOpt as pypfopt
# from pypfopt.efficient_frontier import EfficientFrontier
#
# # optimize2 using cvxpy
# #import cvxpy
#
# # display results
