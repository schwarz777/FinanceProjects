# -*- coding: utf-8 -*-
"""
Created on Mon Oct 14 19:37:30 2019

@author: MichaelSchwarz
"""


class Company:
    """Represents a company, with a ticker."""

    # A class variable, counting the number of Companies
    population = 0

    def __init__(self, ticker):
        """Initializes the company."""
        self.ticker = ticker
        print("(Initializing {})".format(self.ticker))
        Company.population += 1

        "get all keyinputs for this Ticker from mySQL"
        import sys
        sys.path.append(r'C:\Users\MichaelSchwarz\.spyder-py3\myPyCode')
        import MyFuncGeneral as My
        cnx = My.cnx_mysqldb('fuyu_jibengong')
        query = "select Set_name, KeyInput_name,period_end_date,KeyInput_value from v_key_inputs " + \
                "where fk_scope = 1 and reporting_duration_in_months=12 and " + \
                "Ticker_yh='" + ticker + "'"

        import pandas as pd
        self.Fundamentals = pd.read_sql(query, con=cnx)

    def iam(self):
        """introduction of the company"""
        print("I am company", self.ticker)

    def valuation(self, from_date=None):
        """valuation of the company"""
        import pandas_datareader.data as pdr
        import datetime
        to_date = datetime.date.today()
        if not from_date: from_date = to_date - datetime.timedelta(days=1)
        px = pdr.DataReader(self.ticker, 'yahoo', from_date, to_date)

        f = self.Fundamentals

        print("OF COURSE ", 7, f, px)
        # for i in set(f.perod_end_date):

    # =============================================================================
    #         java example not working in py:
    #         switch(f.Set_name) {
    #             case 'Default':  val = 0.1;
    #                      break;
    #             case 'Immo':  val=3;
    #                      break;
    #                              break;
    #             }
    #         print(val)
    #
    # ===============   default: val=None;
    #  ==============================================================

    def die(self):
        """removal of a company"""
        print("Company", self.ticker, "left the universe")
        del self
        Company.population -= 1

    @classmethod
    def how_many(cls):
        """Prints the current number of companes."""
        print("We have {:d} companies.".format(cls.population))


# example
c1 = Company("ABT.TO")
ticker = "ABT.TO"  # for debugging
c1.iam()
c1.valuation()
Company.how_many()
