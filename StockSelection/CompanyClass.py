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

    def __init__(self, CompanyTicker):
        """Initializes the company."""
        self.ticker = CompanyTicker
        Company.instances.append(self)
        print("(Initializing {})".format(self.ticker))
        Company.population += 1

        "get all key inputs for this Ticker from mySQL"
        import sys
        sys.path.append(r'C:\Users\MichaelSchwarz\PycharmProjects\FinanceProjects')
        import MyFuncGeneral as My
        cnx = My.cnx_mysqldb('fuyu_jibengong')
        # get yahoo std data as basic to start with
        query = "select Set_name, KeyInput_name,period_end_date,KeyInput_value from v_key_inputs " + \
                "where source = 'std_yahoo' and reporting_duration_in_months=12 and " + \
                "Ticker_yh='" + CompanyTicker + "'"
        import pandas as pd
        self.Fundamentals = pd.read_sql(query, con=cnx)

    def iam(self):
        """introduction of the company"""
        print("I am company", self.ticker)

    def get_mv(self, as_of=None, source='std_yahoo', keyinputset='Default', liability_keyinput='Liabilities_EV'):
        """calculate the MV  (market value) of the company
            as_of : None for present, date for historic
        """
        if (as_of is None) & (source == 'std_yahoo'):
            last_f = self.Fundamentals[
                (self.Fundamentals['period_end_date'] == max(self.Fundamentals['period_end_date'])) & (
                        self.Fundamentals.Set_name == keyinputset)]
            last_f.KeyInput_value = last_f.KeyInput_value  #  yahoo standardization
            equ_v = last_f.KeyInput_value[last_f.KeyInput_name == 'SharesOutCurrent'].values * My.get_last_close(
                self.ticker)
            ent_v = equ_v + last_f.KeyInput_value[last_f.KeyInput_name == liability_keyinput].values + \
                    last_f.KeyInput_value[
                        last_f.KeyInput_name == 'MinorityInterest_EV'].values
            mv = {'equ_v': equ_v,
                  'ent_v': ent_v}
        else:
            mv = {}
            print("MV for historic and/or non-yahoo-data not defined yet")

        return mv

    def get_KFs(self, keyinputset='Default'):
        """get dif ferent estimates for  Keyfigures depending on v_key_inputs (ie Fundamentals)"""
        f = self.Fundamentals
        f = f[f.Set_name == keyinputset]
        f = f.pivot(index='period_end_date', columns='KeyInput_name')[
            'KeyInput_value']  # transpose inputs for CFs calculation per date
        import pandas as pd
        kf_ = pd.DataFrame()
        kf_type = pd.DataFrame()
        if keyinputset == 'Default':

            # Value estimates
            kf_['AssetBase'] = f['AssetBase']
            kf_type['AssetBase'] = 'Value_estimate'

            kf_['AssetBaseNetCash'] = f['AssetBase'] - f['Cash']
            kf_type['AssetBaseNetCash'] = 'Value_estimate'

            # Debt figures
            kf_['Debt pct'] = f['Liabilities_EV'] / f['AssetBase']
            kf_type['Debt pct'] = 'Value_estimate'

            # CF estimates Entity
            kf_['Operating Earnings'] = f['rR'] + f['rCfix']
            kf_type['Operating Earnings'] = 'CF_est_Ent'

            kf_['Operating Earnings incl non-core'] = kf_['Operating Earnings'] + f['ncIt']
            kf_type['Operating Earnings and non-core'] = 'CF_est_Ent'

            kf_['Operating Earnings after capex'] = kf_['Operating Earnings'] + f['capex']
            kf_type['Operating Earnings after capex'] = 'CF_est_Ent'

            # CF estimates Equity
            kf_['Operating Earnings Equ'] = (kf_['Operating Earnings'] + f['rCinterest'] + f['rRinterest']) * (
                    1 - f['tax rate'])
            kf_type['Operating Earnings Equ'] = 'CF_est_Equ'

            kf_['Operating Earnings after capex Equ'] = (kf_['Operating Earnings'] + f['rCinterest'] + f[
                'rRinterest']) * (1 - f['tax rate']) + f['capex']
            kf_type['Operating Earnings after capex Equ'] = 'CF_est_Equ'

            kf_['Operating Earnings incl non-core Equ'] = (kf_['Operating Earnings incl non-core'] + f['rCinterest'] +
                                                           f['rRinterest']) * (1 - f['tax rate'])
            kf_type['Operating Earnings incl non-core Equ'] = 'CF_est_Equ'

            kf_['NetIncome'] = f['NetIncome_reported']
            kf_type['NetIncome'] = 'CF_est_Equ'

            kf_['operating CF'] = f['operatingCF_reported']
            kf_type['operating CF'] = 'CF_est_Equ'

            kf_['operating CF after capex'] = kf_['operating CF'] + f['capex']
            kf_type['operating CF after capex'] = 'CF_est_Equ'
        else:
            print("not defined how to handle keyinputset '" + keyinputset + "' yet")

        return {'KFs': kf_, 'KFs_type': kf_type}

    # def get_FV(self, historic_since=None,keyinputset='Default'): #used parameters to filter from v_key_inputs: Set, statement (+ make a check that not 2statements for same item!!!), then  group by period end (annualize if necessary!)
    #     """calculate FV(s) of the company"""
    #     # base on data from
    #     # set
    #     import pandas_datareader.data as pdr
    #     import datetime
    #     to_date = datetime.date.today()
    #     if not historic_since:
    #         from_date = to_date #- datetime.timedelta(days=1)
    #     else:
    #         print("historic valuation still to be implemented")
    #
    #
    #     f = self.Fundamentals
    #
    #     # for i in set(f.perod_end_date):
    #         #switch keyinputset (which defines the calculationmethod for the keyfig_set
    #
    #         #return keyfigset (consisting of dicts (date, keyfig, scope)

    def get_valuation(self, displayMethod='YtFV', discountRate=None):
        """
        displayMethod must be in: 'YtFV' (Yield to FairValue), 'Premium/discount', 'Multiple'

        require(displayMethod in ['YtFV' ,'Premium/discount','Multiple'])
        require( displayMethod in ['YtFV' ,'Premium/discount'] & discountRate != None) #only for Multiple no discountRate is required


        Parameters
        ----------
        here simply get FV and MV and calculate valuation properly!

        Returns
        -------

        """
        # divide FV by

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
    @classmethod
    def compare(cls, start, end,
                normalize_by='shortest'):  # add: ,comparison_way=prices, prices normalized, prices_to_invest,valuations,...
        """plots the current members of Companies in the defined way"""
        import sys
        sys.path.append(r'C:\Users\MichaelSchwarz\PycharmProjects\FinanceProjects')
        import MyFuncGeneral as My
        tickers = {instance.ticker for instance in cls.instances}
        df = My.get_tickers_history(start, end, tickers, 'Close', normalize_by=normalize_by)
        import plotly.graph_objects as go
        fig_to_plot = go.Figure([{
            'x': df.index,
            'y': df[col],
            'name': col
        } for col in df.columns])
        return fig_to_plot

    @staticmethod
    def remove_all_companies():
        Company.instances = []
        Company.population = 0


if __name__ == '__main__':
    Company.remove_all_companies()
    #  ticker = ["URW.AS","LI.PA","VALN.SW","FHZN.SW"] # for debugging
    #  for i in ticker:
    #      i = Company(i)
    #  #c1 = Company("IES.L")
    #  CurrentUniverse = {id(instance): instance.ticker for instance in Company.instances}
    #  Company.how_many()
    #  Company.compare(start="2015-01-05", end="2020-08-12")
    #  fig = i.compare(start="2020-01-05", end="2020-08-12")
    #  fig.show()

    ticker = "NESN.SW"
    N = Company(ticker)
    mv = N.get_mv()
    A = Company('ALB')
    mvA = A.get_mv()
    kf = A.get_KFs()
    kf['KFs'].transpose()
#   tickers = {instance.ticker for instance in Company.instances}
#  print(CurrentUniverse)
# print(c1.Fundamentals)
