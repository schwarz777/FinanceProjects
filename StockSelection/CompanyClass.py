# -*- coding: utf-8 -*-
"""
Created on Mon Oct 14 19:37:30 2019

@author: MichaelSchwarz

how it is embedded in framework and overview of processes: https://app.diagrams.net/#G1JGE9l-BotVV2vmpVJIEaInXLLW4A0_Rs
"""
import sys
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import xarray as xr
import datetime as dt
sys.path.append(r'C:\Users\MichaelSchwarz\PycharmProjects\FinanceProjects')
import MyFuncGeneral as My
sys.path.append(r'C:\Users\MichaelSchwarz\PycharmProjects\FinanceProjects\StockSelection')
import yahoo_fundamentals as yhf

#todo: find way to avoid double company instsances:
# def multiton(cls):
#    instances = {}
#    def getinstance(id):
#       if id not in instances:
#          instances[id] = cls(id)
#       return instances[id]
#    return getinstance
#
# @multiton
class Company():
    """Represents a company, with a ticker."""
    # A class variable, counting the number of Companies
    #instances = []
    population = 0

    def __init__(self, CompanyTicker):  # future parameter datasource as here the selection of the datasource happens
        """Initializes the company."""
        self.id = CompanyTicker
        self.ticker = CompanyTicker
        Company.instances.append(self)
        print("(Initializing {})".format(self.ticker))
        Company.population += 1

        # "get all key inputs for this Ticker from mySQL"
        cnx = My.cnx_mysqldb('fuyu_jibengong')
        # get yahoo std data as basic to start with
        query = "select Set_name, KeyInput_name,period_end_date,KeyInput_value " \
                "from v_key_inputs_with_scenarios " + \
                "where source = 'std_yahoo' and reporting_duration_in_months=12 and " + \
                "Ticker_yh='" + CompanyTicker + "' and " + \
                "scenario_name = 'None' "
        # todo: dont filter for scenario_name but build scenario alternative properly!!!
        self.Fundamentals = pd.read_sql(query, con=cnx)
        if(self.Fundamentals.empty):
            yhf.update_db(self.ticker,addLackingFK=True)
        #elif(dt.year(max(self.Fundamentals.index)) < 2019 )
        self.Fundamentals = pd.read_sql(query, con=cnx)

    def iam(self):
        """introduction of the company"""
        print("I am company", self.ticker)

    def get_mv(self, hist_since=None,  keyinputset='Default',
               price_source='std_yahoo',liability_keyinput='Liabilities_EV'):
        """calculate the MV  (market value) of the company
            hist_since : None for present, date for historic date value like hist_since = '2018-09-01'
        """
        if 'std_yahoo' != price_source:
            raise ValueError('Only source std_yahoo defined. You gave: ', price_source)
        kid = self.pivot_keyinputs_of_set(keyinputset)  # get pivotted key input data
        if hist_since is None:
            last_f = kid.loc[kid.index == max(kid.index), :]
            equ_v = My.get_last_close(self.ticker) * last_f['SharesOutCurrent'].to_numpy()
            ent_v = equ_v + last_f[liability_keyinput].to_numpy() + last_f['MinorityInterest_EV'].to_numpy()
            mv = {'equ_v': equ_v,
                  'ent_v': ent_v}
        else:
            p_close = My.get_tickers_history(tick_list=[self.ticker], start=hist_since)
            close_w_fundamentals = My.fill_up_series_with_closest(long_series=p_close.iloc[:, 0], short_series=kid)
            equ_v = close_w_fundamentals.iloc[:, 0] * close_w_fundamentals["SharesOutCurrent"]
            ent_v = equ_v + close_w_fundamentals[liability_keyinput] + close_w_fundamentals[
                'MinorityInterest_EV'].fillna(0)
            mv = {'equ_v': equ_v,
                  'ent_v': ent_v}
        return mv
        #example
        #hist_since='2019-12-31';  keyinputset='Default'; price_source='std_yahoo' ; liability_keyinput='Liabilities_EV'


    def pivot_keyinputs_of_set(self, chosen_set='Default'):
        f = self.Fundamentals
        f = f[f.Set_name == chosen_set]
        f = f.pivot(index='period_end_date', columns='KeyInput_name')[
            'KeyInput_value']  # transpose inputs for CFs calculation per date
        # tricky: add company spec scenarios!!!
        return f

    # def get_kf_valuations(self,keyinputset='Default',displayMethod='YtFV', discountRate=None, exclude_hist_val=False):
    # wrapper to loop through all KFs and get the desired valuation for it

    # def get_FV(self, historic_since=None,keyinputset='Default'):
    # used parameters to filter from v_key_inputs: Set, statement
    # (+ make a check that not 2statements for same item!!!), then  group by period end (annualize if necessary!)
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

    @classmethod
    def current_population_members(cls):
        memb = {instance.ticker for instance in cls.instances}
        return list(memb)

    @classmethod
    def get_mvs(cls, price_source='std_yahoo', keyinputset='Default', liability_keyinput='Liabilities_EV',
                hist_dates=None):
        """get the market values for each instance in the class and put it in a dataframe """
        all_companies = cls.instances
        if hist_dates is not None:
            initialize_output_array = True
            for i in all_companies:
                if initialize_output_array:
                    try:
                        mv_i = i.get_mv(price_source=price_source, hist_since=min(hist_dates))
                        equ_vs = pd.DataFrame(columns=cls.current_population_members(),index = hist_dates.insert(len(hist_dates),mv_i['equ_v'].index[-1]))
                        ent_vs = pd.DataFrame(columns=cls.current_population_members(),index = hist_dates.insert(len(hist_dates),mv_i['ent_v'].index[-1]))
                                            #empty df can be the same + like this lacking ent-values in first tickers dont cause
                        equ_vs[i.ticker] = pd.merge_asof(equ_vs[i.ticker].to_frame(), mv_i['equ_v'].to_frame(),
                                                         left_index=True, right_index=True,
                                                         direction='backward').iloc[:, 1]

                        ent_vs[i.ticker] = pd.merge_asof(ent_vs[i.ticker].to_frame(), mv_i['ent_v'].to_frame(),
                                                         left_index=True, right_index=True,
                                                         direction='backward').iloc[:, 1]
                        initialize_output_array = False
                    except:
                        initialize_output_array = True #just do initialization with next run
                        print("for company "+i.ticker+" not enough fundamental data found, output initialisation will be done next run")
                else:
                    try:
                        mv_i = i.get_mv(price_source=price_source,hist_since=min(hist_dates))
                        #assign latest market values to periods by merge operation (focusing just on the 2nd column of the merge)
                        equ_vs[i.ticker] = pd.merge_asof(equ_vs[i.ticker].to_frame(),mv_i['equ_v'].to_frame(),
                                                     left_index=True,right_index=True,direction='backward').iloc[:,1]

                        ent_vs[i.ticker] = pd.merge_asof(ent_vs[i.ticker].to_frame(),mv_i['ent_v'].to_frame(),
                                                     left_index=True,right_index=True,direction='backward').iloc[:,1]
                    except:
                        print("for company "+i.ticker+" not enough fundamental data found to calculate MVs")
                mv_i = []
        else:
            # define output tables
            equ_vs = pd.DataFrame(columns=cls.current_population_members())
            ent_vs = pd.DataFrame(columns=cls.current_population_members())
            for i in all_companies:
                try:
                    mv_i = i.get_mv(price_source=price_source, keyinputset=keyinputset, liability_keyinput=liability_keyinput)
                    equ_vs[i.ticker] = mv_i['equ_v'].values
                    ent_vs[i.ticker] = mv_i['ent_v'].values
                    mv_i = []
                except:
                    print("for company " + i.ticker + " not enough fundamental data found to calculate MVs")
        MVs = {'ent_v': ent_vs,
               'equ_v': equ_vs}
        return (MVs)
        # example
        # cls = Company
        # price_source = 'std_yahoo'; keyinputset = 'Default'; liability_keyinput = 'Liabilities_EV';
        # hist_dates = cls.get_kf('NetIncome').index#.date
        # mvs = get_mvs(cls,hist_dates=hist_dates);type(mvs['ent_vs'])

    @classmethod
    def compare(cls, start, end,
                normalize_by='shortest'):  # add: ,comparison_way=prices, prices normalized, prices_to_invest,valuations,...
        """plots the current members of Companies in the defined way"""
        tickers = cls.current_population_members()
        df = My.get_tickers_history(tick_list = list(tickers), start=start, end=end, this_price='Close',
                                    normalize_by=normalize_by)

        fig_to_plot = go.Figure([{
            'x': df.index,
            'y': df[col],
            'name': col
        } for col in df.columns])
        return fig_to_plot

    @classmethod
    def get_vals(cls, chosen_kfs, keyinputset='Default', displayMethod='YtFV', WACC=None):
        """wrapper to loop through and calcualte the valuations for the whole population with respect to the KFs desired  !
            ----------
            Returns Valuation for the whole population (per company year/scenario)
            -------
        """
        kf_mv_lu = {
            'AssetBase': 'ent_v',

            'Operating Earnings': 'ent_v',
            'Operating Earnings incl non-core': 'ent_v',
            'Operating Earnings after capex': 'ent_v',

            'Operating Earnings Equ': 'equ_v',
            'Operating Earnings Equ incl non-core': 'equ_v',
            'Operating Earnings after capex Equ': 'equ_v',
            'NetIncome': 'equ_v',
            'operating CF': 'equ_v',
            'operating CF after capex': 'equ_v'
            # 'Debt_figure'
        }
        # start calculation KF by kf

        initialize = True
        for kf in chosen_kfs:
           try:
                assert (kf in kf_mv_lu)
                print("start calculation for keyfigure " + kf)
                this_kf = cls.get_kf(kf,keyinputset=keyinputset)
                if initialize == True:
                    hist_dates=this_kf.index
                    companies = this_kf.columns
                    mvs=cls.get_mvs(hist_dates=hist_dates,keyinputset=keyinputset)
                    periods = mvs['equ_v'].index
                    empty_arr = np.full(fill_value=np.nan,shape=(len(periods),len(chosen_kfs),len(companies)))
                    VAL = xr.DataArray(data=empty_arr, dims=["period", "kf", "company"],
                                       coords=[("period", periods),
                                               ("kf", chosen_kfs),
                                               ("company", companies) ]
                                       )
                    initialize = False


                VAL.loc[:,kf,:] = cls.get_val(kfv=this_kf,mvs= mvs,kftype = kf_mv_lu[kf], CoD=0.02,displayMethod=displayMethod, WACC=WACC)
                print("successfully finished calculation for keyfigure '" + kf +"'")
           except:
                print("kf '"+ kf +"' could not be calculated and remains set to na. Is it a non-defined kf?")
        print("sucessfully finished valuations based on required kfs")
        return VAL
        # example
        #chosen_kfs = ['NetIncome', 'AssetBase', 'Operating Earnings'];  keyinputset='Default';displayMethod='YtFV';WACC=None
        #cls = Company

    @classmethod
    def get_val(cls, kfv:pd.DataFrame, mvs:dict,kftype:str, CoD=0.02, displayMethod='YtFV', WACC=None):
        """get valuation based on keyfigure_value, market value and method, based on certain WACC.
            A class function as in the relative framework it might well be necessary to perform it simultaneously on the
            whole population to estimate 'population WACC' (then derive the proper equity and entity discount figures
            for the single companies.)

           Parameters:
           * kfv: keyfigure value of a specific kf (can be a time series)
           * mvs: equity and entity values of the companies (can be time series)
           # kftype: type of keyfigure (mainly ent or equ)
           * CoD_default: default value for cost of debt. is taken if incomplete CoD-estimates from companies available
             Todo: should be made dynamic in some way, clearly changing over time! incorporate Tax in WACC-calc
           * displayMethod specifies how to relate kfv and mv.
             It must be in: 'YtFV' (Yield to FairValue), 'Premium/discount', 'Multiple','Other'
           * WACC: Weighted average cost of debt. If none it will be calculated to match a fair valuation on the
           population with respect to the kf to value. This means different WACCs result for different kfs
           FORMULA: WACC = (equ_v / ent_v) × CoE + (D / ent_v) × CoD × (1 − tax)
           Fair Valuation defined as: kf_ent/WACC = EV  (assuming kf_ent = infinite CF to the company)
           kf_ent for equity kf: kf + Debt * CoD =kf_ent
        """
        assert(displayMethod in ['YtFV' , 'Premium/discount', 'Multiple','Other'])
        assert(kftype in ['equ_v','ent_v'])
        assert (WACC is None or WACC == 'hist' or isinstance(WACC, float))

        #project kfv in the future if still lacking
        kfv.loc[max(mvs['equ_v'].index)]=kfv.loc[max(kfv.index),:]

        #get parameters for rate calculations
        ent_v = mvs['ent_v']
        equ_v = mvs['equ_v']
        D = ent_v - equ_v
        if WACC != 'hist':
            ent_v = ent_v.iloc[-1,:]
            equ_v = equ_v.iloc[-1, :]
            D = D.iloc[-1,:]

        #get discount rate needed
        #get WACC if needed
        if WACC is None or WACC == 'hist':
            #define entity value
            if kftype == 'equ_v':
                kfv_ent = kfv+D*CoD
            else:
                kfv_ent = kfv
            #calculate WACC on present or hist FVs and MVs: average across population is taken
            if WACC == 'hist':
                WACC_companies = kfv_ent/ent_v
                WACC=WACC_companies.transpose().mean()
            else:
                WACC_companies = kfv_ent.iloc[-1,:]/ent_v
                WACC = WACC_companies.transpose().mean()

        #calculate equity discount rates if needed (depending on comapny leverage)
        if kftype == 'equ_v':
            #WACC = (equ_v / ent_v) × CoE + (D / ent_v) × CoD × (1 − tax)
            #leads to (D=ent_v-equ_v):
            #CoE = ent_v/eq_v *(WACC-CoD*(1-tax)) + CoD * (1-tax)
            tax = 0.15
            CoE = (ent_v/equ_v).mul(WACC-CoD*(1-tax),axis=0) +CoD*(1-tax)
            fv = kfv / CoE
            p =  mvs['equ_v']
        else:
            fv = kfv.div(WACC,axis=0)
            p =  mvs['ent_v']

        #return the signal s based on chosen displayMethod
        if (displayMethod == 'YtFV'):
            s = fv / p -1
        elif (displayMethod == 'Premium'):
            s = p / fv -1
        elif (displayMethod == 'Multiple'):
            s = p / kfv
        else:
            print("unspecified display Method selected")
        return(s)
        #example
        #cls=Company;kfv =cls.get_kf('NetIncome');mvs = cls.get_mvs(hist_dates=kfv.index);CoD=0.02; displayMethod='YtFV'
        #WACC = 'hist'

    @classmethod
    def get_kf(cls, kf, keyinputset='Default'):
        """get different estimates for  Keyfigures depending on v_key_inputs_from_scenarios (ie Fundamentals)"""
        # here the  logic on keyfigure calculation based on keyinputs is defined!
        # each keyfigure is calculated for the whole population and across as certain inputs might be derived from population/historic  averages/medians!)

        all_companies = cls.instances
        all_tickers = cls.current_population_members()
        assert (keyinputset == 'Default')  # calculation still needs to be defined for other keyinputsets -> aim for a more generic structure (where a get_set_kf function can be created!)

        #collect  keyinput_information for all companies into ki_a
        initialize_output_array = True
        for comp in all_companies:
            try:
                ki = comp.pivot_keyinputs_of_set(chosen_set=keyinputset)  # keyinputs
                if initialize_output_array:
                    # initialize 3d Dataframe to store keyinput data (kid)
                    # do with select distinct?
                    empty_arr = np.full(fill_value=np.nan,shape=(len(ki.index),len(ki.columns),len(all_companies)))
                    keyinputs = ki.columns.values
                    periods = ki.index.values
                    #put ki into 3d array for all keyinputs ki_a
                    ki_a = xr.DataArray(data=empty_arr, dims=[ "period","keyinput","company"],
                                           coords=[("period", periods),("keyinput", keyinputs),("company",all_tickers)
                                       ])  # xr.Dataset() #http://xarray.pydata.org/en/stable/pandas.html#pandas
                    #ki_a = xr.DataArray(kid,dims=[ "keyinput", "period","company"])
                    initialize_output_array = False

                else:
                    #check if ki_a still accomodates all periods and keyinputs
                    lacking_columns=np.setdiff1d(np.array(ki.columns) , np.array(ki_a.get_index("keyinput")))
                    lacking_periods = np.setdiff1d(np.array(ki.index), np.array(ki_a.get_index("period")))
                    if len(lacking_columns)>0 or len(lacking_periods)>0:
                        if len(lacking_columns)>0:
                            #add lacking keyinput into ki_a
                            empty_fill_arr = np.full(fill_value=np.nan,shape=(len(ki_a.get_index("period")),1,len(ki_a.get_index("company"))))
                            for lc in lacking_columns:
                                this_empty_fill_arr = xr.DataArray(data=empty_fill_arr, dims=[ "period","keyinput","company"],
                                                        coords=[("period", periods),("keyinput", np.array([lc])),("company",all_tickers)
                                                        ])
                                ki_a = xr.concat([ki_a,this_empty_fill_arr],dim="keyinput")
                            keyinputs = ki_a.get_index("keyinput").values
                        elif len(lacking_periods)>0:
                            #add lacking periods into ki_a
                            empty_fill_arr = np.full(fill_value=np.nan,shape=(1, len(ki_a.get_index("keyinput")), len(ki_a.get_index("company"))))
                            for lp in lacking_periods:
                                this_empty_fill_arr = xr.DataArray(data=empty_fill_arr, dims=["period", "keyinput", "company"],
                                                        coords = [("period", np.array([lp])), ("keyinput",keyinputs ), ("company", all_tickers)
                                                ])
                                ki_a = xr.concat([ki_a, this_empty_fill_arr], dim="period")
                            periods = ki_a.get_index("period").values
                    else:
                        None
                        #nothing to do the ki_a - array also fits ki of this company
                ki_a.loc[ki.index, ki.columns, comp.ticker] = ki
            except:
                print("loading for company " + comp.ticker + " failed - na values set instead")
           # ki_a.loc[:, :, comp.ticker].to_pandas()
        # todo calc  avg  across sections time for use to calc certain figures!
        # start to calculate kf values across periods and companies (simultaneously from 3d ki_a!)
        def ki_ (ki,Na2Zero=True):
            ki = ki_a.loc[:,ki,:].to_pandas()
            if Na2Zero:
                ki = ki.fillna(0)
            return ki

        try:  #calculation will only work if the required keyinputs are there for at least some companies!
            if kf in ['AssetBase']:
                if kf == 'AssetBase':
                    kf_val = ki_('AssetBase',Na2Zero=False)
            # elif keyfigure in ['Debt pct']:
            # # Debt figures
            # kf_['Debt pct'] = f['Liabilities_EV'] / f['AssetBase']
            # kf_type['Debt pct'] = 'Debt_figure'
            elif kf in ['Operating Earnings', 'Operating Earnings incl non-core', 'Operating Earnings after capex']:
                op_earn_ent = ki_('rR',Na2Zero=False) + \
                              ki_('rCvar')  +ki_('rCfix') # basic buildidng block for CF estimates Ent
                if kf == 'Operating Earnings':
                    kf_val = op_earn_ent
                elif kf == 'Operating Earnings incl non-core':
                    kf_val = op_earn_ent + ki_('ncIt')
                elif kf == 'Operating Earnings after capex':
                    kf_val = ki_('rR') + ki_('rCfix') + ki_('capex',Na2Zero=False)
            elif kf in ['Operating Earnings Equ', 'Operating Earnings Equ incl non-core', 'Operating Earnings after capex Equ']:
                # basic building blocks for above CF estimates Equity
                op_earn_equ_ex_t = ki_('op_earn_ent') +\
                                   ki_('rCinterest') + \
                                   ki_('rRinterest')# eq earning before tax
                tax = ki_('tax rate')
                # calc different CF estimates Equity
                if kf == 'Operating Earnings Equ':
                    kf_val = op_earn_equ_ex_t * (1 - tax)
                elif kf == 'Operating Earnings Equ incl non-core':
                    kf_val = (op_earn_equ_ex_t + ki_('ncIt')) * (1 - tax)
                elif kf == 'Operating Earnings after capex Equ':
                    kf_val = (op_earn_equ_ex_t + ki_('capex',Na2Zero=False)) * (1 - tax)
            elif kf in ['NetIncome', 'operating CF', 'operating CF after capex']:
                if kf == 'NetIncome':
                    kf_val = ki_('NetIncome_reported',Na2Zero=False)
                elif kf == 'operating CF':
                    kf_val = ki_('operatingCF_reported',Na2Zero=False)
                elif kf == 'operating CF after capex':
                    kf_val = ki_('operatingCF_reported',Na2Zero=False) + ki_('capex',Na2Zero=False)
            else:
                print("undefined keyfigure specified. Typo????")
            # else:
            #     print("not defined how to handle keyinputset '" + keyinputset + "' yet")
        except KeyError as e:
            print("the KF '"+ kf +"' cannot be calculated as keyinput '"  + e.args[0] + "' is lacking")
            #todo define Nan value for kf_val
        except:
            print(kf+"could not be calculated")
        return kf_val

        # example
        # cls = Company
        # kf='Operating Earnings'

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
    N = Company("NESN.SW")
    T = Company("TRUP")
    G=Company("GUR.SW")
    mv_N = N.get_mv()
    A = Company('ALB')
    mvA = N.get_mv()
    f_pvt = N.pivot_keyinputs_of_set()
    f_pvtA=A.pivot_keyinputs_of_set()
    N.get_kf('NetIncome')
    mv_now = Company.get_mvs()
    mv_all=N.get_mvs(hist_dates = f_pvt.index)
    kf_all=Company.get_kf('AssetBase')
    ytfv=N.get_val(kf_all,mv_all,'equ_v')
    ytfv.plot()
    V=Company.get_vals(['NetIncome', 'AssetBase'])#, 'Operating Earnings'])
    V[:,:,0].to_pandas().plot()

    all_kf=['AssetBase','Operating Earnings', 'Operating Earnings incl non-core', 'Operating Earnings after capex','Operating Earnings Equ', 'Operating Earnings Equ incl non-core', 'Operating Earnings after capex Equ','NetIncome', 'operating CF', 'operating CF after capex']
    Vall=Company.get_vals(all_kf)
    Vall.loc[:,'AssetBase', :].to_pandas().plot()
    #radar plot or parallel coordinates plot.
    #https://xarray-contrib.github.io/xarray-tutorial/scipy-tutorial/04_plotting_and_visualization.html
