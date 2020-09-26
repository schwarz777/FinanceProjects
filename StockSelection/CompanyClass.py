# -*- coding: utf-8 -*-
"""
Created on Mon Oct 14 19:37:30 2019

@author: MichaelSchwarz
"""
class KF:
    """Keyfigure: defined by name with attributes value (list of dates and respective values) and kf_type"""
    def __init__(self, name, value, kf_type):
         self.name = name
         #assert value is pd.df table with years and (numeric) values
             # import sys
             # sys.path.append(r'C:\Users\MichaelSchwarz\PycharmProjects\FinanceProjects')
             # import MyFuncGeneral as My
             # My.check_numeric(value)
         self.value = value
         assert kf_type in ['Value_estimate','Debt_figure','CF_est_Ent','CF_est_Equ']
         self.type = kf_type

    def get_valuation(self, mv, displayMethod='YtFV', discountRate=None, include_hist_val=False):
            """
            here simply use FV and MV and calculate valuation as specified!
            displayMethod must be in: 'YtFV' (Yield to FairValue), 'Premium/discount', 'Multiple'

            require(displayMethod in ['YtFV' ,'Premium/discount','Multiple'])
            require( displayMethod in ['YtFV' ,'Premium/discount'] & discountRate != None) #only for Multiple no discountRate is required

            ----------
            Returns
            -------

            """
            if displayMethod == 'YtFV':
                #
                def get_keyfigure(val):
                    for key, value in kf['KFs_type'].items():
                        if val == value:
                            return key

                    return "key doesn't exist"

                get_keyfigure('Value_estimate')

                get_keyfigure('CF_est_Ent')
            else:
                print("display Method '"+displayMethod +"' not yet implemented")

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
        # TODO: check if update needed!

    def iam(self):
        """introduction of the company"""
        print("I am company", self.ticker)

    def get_mv(self, as_of=None, source='std_yahoo', keyinputset='Default', liability_keyinput='Liabilities_EV'):
        """calculate the MV  (market value) of the company
            as_of : None for present, date for historic
        """
        sys.path.append(r'C:\Users\MichaelSchwarz\PycharmProjects\FinanceProjects')
        import MyFuncGeneral as My

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

    def get_kfs(self, keyinputset='Default'):
        """get dif ferent estimates for  Keyfigures depending on v_key_inputs (ie Fundamentals)"""
        f = self.Fundamentals
        f = f[f.Set_name == keyinputset]
        f = f.pivot(index='period_end_date', columns='KeyInput_name')['KeyInput_value']  # transpose inputs for CFs calculation per date

        #help functions to get valid keyfig-columns only (any missing input -> None-Keyfig)
        def get_col(colname,f=f,sign=1):
            if colname in f.columns:
                #todo check structure
                col_out =sign*f[colname]
            else:
                col_out = None
            return col_out

        def sum_or_none(list):
            if not any(x is None for x in list):
                if len(list) == 1:
                    s = list[0]
                else:
                    s = sum(list)
            else:
                s=None
            return s

        # start calculating the keyfigures and put them in KFs
        KFs = []
        if keyinputset == 'Default':
            # Value estimates
            kf_type = 'Value_estimate'
            kf_is_sum = [get_col(colname='AssetBase')]
            KFs.append(KF('AssetBase',sum_or_none(kf_is_sum),kf_type))
            kf_is_sum.append(get_col('Cash',sign=-1))
            KFs.append(KF('AssetBaseNetCash',sum_or_none(kf_is_sum),kf_type))

            # # Debt figures
            # kf_['Debt pct'] = f['Liabilities_EV'] / f['AssetBase']
            # kf_type['Debt pct'] = 'Debt_figure'

            # CF estimates Entity
            kf_type = 'CF_est_Ent'
            kf_is_sum = [get_col('rR') , get_col('rCfix') ]
            op_earn_ent = sum_or_none(kf_is_sum)
            KFs.append(KF('Operating Earnings',op_earn_ent,kf_type))


            op_earn_ent_nc = sum_or_none([op_earn_ent,get_col('ncIt')])
            KFs.append(KF('Operating Earnings and non-core', sum_or_none(kf_is_sum), kf_type))

            kf_is_sum = [get_col('rR'), get_col('rCfix'),get_col('capex')]
            KFs.append(KF('Operating Earnings after capex', sum_or_none(kf_is_sum), kf_type))

            # CF estimates Equity
            kf_type = 'CF_est_Equ'
            kf_is_sum = [op_earn_ent,get_col('rCinterest'),get_col('rRinterest')]
            earn_ex_tax = sum_or_none(kf_is_sum)
            kf_is_sum = [op_earn_ent_nc, get_col('rCinterest'), get_col('rRinterest')]
            earn_ex_tax_nc = sum_or_none(kf_is_sum)
            if get_col('tax rate') is None:
                print("no tax rate -> 0taxes assumed")
                earn=earn_ex_tax
                earn_nc = earn_ex_tax_nc

            else:
                earn = earn_ex_tax*(1-get_col('tax rate'))
                earn_nc = earn_ex_tax_nc*(1-get_col('tax rate'))


            KFs.append(KF('Operating Earnings Equ', earn, kf_type))
            KFs.append(KF('Operating Earnings incl non-core', earn_nc, kf_type))
            earn_cpx = sum_or_none([earn,get_col('capex')])
            KFs.append(KF('Operating Earnings after capex Equ', earn_cpx, kf_type))

            KFs.append(KF('NetIncome', get_col('NetIncome_reported'), kf_type))

            KFs.append(KF('operating CF', get_col('operatingCF_reported'), kf_type))

            kf_is_sum = [get_col('operating CF'),get_col('capex')]
            KFs.append(KF('operating CF after capex', sum_or_none(kf_is_sum), kf_type))

        else:
            print("not defined how to handle keyinputset '" + keyinputset + "' yet")

        return KFs

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
    mvA = N.get_mv()
    kf = A.get_kfs()
    kf['KFs'].transpose()
#   tickers = {instance.ticker for instance in Company.instances}
#  print(CurrentUniverse)
# print(c1.Fundamentals)
