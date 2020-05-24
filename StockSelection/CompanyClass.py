# -*- coding: utf-8 -*-
"""
Created on Mon Oct 14 19:37:30 2019

@author: MichaelSchwarz
"""


class Company:
    """Represents a company, with a ticker."""
    # A class variable, counting the number of Companies
    instances = []
    population = 0

    def __init__(self, ticker):
        """Initializes the company."""
        self.ticker = ticker
        Company.instances.append(self)
        print("(Initializing {})".format(self.ticker))
        Company.population += 1

        "get all keyinputs for this Ticker from mySQL"
        import sys
        sys.path.append(r'C:\Users\MichaelSchwarz\PycharmProjects\FinanceProjects')
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
        if not from_date:
            from_date = to_date - datetime.timedelta(days=1)
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
        Company.instances.remove(self)
        del self
        Company.population -= 1

    @classmethod
    def how_many(cls):
        """Prints the current number of companies."""
        print("We have {:d} companies.".format(cls.population))
    # def remove_all_companies():
    #     instance.die() or instance in Company.instances
    def  compare(cls, start, end):  ##add: ,comparison_way=prices, prices normalized, prices_to_invest,valuations,...
        """plots the current members of Companies in the defined way"""
        import sys
        sys.path.append(r'C:\Users\MichaelSchwarz\PycharmProjects\FinanceProjects')
        import MyFuncGeneral as My
        tickers = {instance.ticker for instance in Company.instances}
        My.get_tickers_history(start, end, tickers, 'Close').plot()


if __name__ == '__main__':
    ticker = "IBM"  # for debugging
    c1 = Company(ticker)
    c1.iam()
    c1.valuation()
    CurrentUniverse = {id(instance): instance.ticker for instance in Company.instances}
    Company.how_many()
    Company.compare(Company, start="2019-01-05", end="2020-05-25")
    print(CurrentUniverse)
    print(c1.Fundamentals)

    # Todo: Company.remove_all_companies()