from datetime import datetime
import lxml
from lxml import html
import requests
import numpy as np
import pandas as pd
import sys
import datetime as dt


# description of code: https://www.mattbutton.com/2019/01/24/how-to-scrape-yahoo-finance-and-extract-fundamental-stock-market-data-using-python-lxml-and-pandas/

def get_page(url):
    # Set up the request headers that we're going to use, to simulate
    # a request by the Chrome browser. Simulating a request from a browser
    # is generally good practice when building a scraper
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.9',
        'Cache-Control': 'max-age=0',
        'Pragma': 'no-cache',
        'Referrer': 'https://google.com',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36'
    }

    return requests.get(url, headers=headers)


def parse_rows(table_rows):
    parsed_rows = []

    for table_row in table_rows:
        parsed_row = []
        el = table_row.xpath("./div")

        none_count = 0

        for rs in el:
            try:
                (text,) = rs.xpath('.//span/text()[1]')
                parsed_row.append(text)
            except ValueError:
                parsed_row.append(np.NaN)
                none_count += 1

        if (none_count < 4):
            parsed_rows.append(parsed_row)

    return pd.DataFrame(parsed_rows)


def clean_data(df):
    df = df.set_index(0)  # Set the index to the first column: 'Period Ending'.
    df = df.transpose()  # Transpose the DataFrame, so that our header contains the account names

    # Rename the "Breakdown" column to "Date"
    cols = list(df.columns)
    cols[0] = 'Date'
    df = df.set_axis(cols, axis='columns', inplace=False)

    numeric_columns = list(df.columns)[1::]  # Take all columns, except the first (which is the 'Date' column)

    for column_index in range(1, len(df.columns)):  # Take all columns, except the first (which is the 'Date' column)
        df.iloc[:, column_index] = df.iloc[:, column_index].str.replace(',', '')  # Remove the thousands separator
        df.iloc[:, column_index] = df.iloc[:, column_index].astype(np.float64)  # Convert the column to float64

    return df


def scrape_table(url):
    # Fetch the page that we're going to parse
    page = get_page(url);

    # Parse the page with LXML, so that we can start doing some XPATH queries
    # to extract the data that we want
    tree = html.fromstring(page.content)

    # Fetch all div elements which have class 'D(tbr)'
    table_rows = tree.xpath("//div[contains(@class, 'D(tbr)')]")

    # Ensure that some table rows are found; if none are found, then it's possible
    # that Yahoo Finance has changed their page layout, or have detected
    # that you're scraping the page.
    assert len(table_rows) > 0

    df = parse_rows(table_rows)
    df = clean_data(df)

    return df


def scrape(symbol):
    print('Attempting to scrape data for ' + symbol)

    df_balance_sheet = scrape_table('https://finance.yahoo.com/quote/' + symbol + '/balance-sheet?p=' + symbol)
    df_balance_sheet = df_balance_sheet.set_index('Date')

    df_income_statement = scrape_table('https://finance.yahoo.com/quote/' + symbol + '/financials?p=' + symbol)
    df_income_statement = df_income_statement.set_index('Date')

    df_cash_flow = scrape_table('https://finance.yahoo.com/quote/' + symbol + '/cash-flow?p=' + symbol)
    df_cash_flow = df_cash_flow.set_index('Date')

    df_joined = df_balance_sheet \
        .join(df_income_statement, on='Date', how='outer', rsuffix=' - Income Statement') \
        .join(df_cash_flow, on='Date', how='outer', rsuffix=' - Cash Flow') \
        .dropna(axis=1, how='all') \
        .reset_index()

    df_joined.insert(1, 'Symbol', symbol)

    return df_joined


def update_db(symbol, addLackingFK=False):
    """ update the mysql data with possible newer data """
    df = scrape(symbol)
    for t in df['Date']:
        updi = df.loc[df['Date'] == t]
        updi = updi.iloc[:, 3:]
        if t != 'ttm':  # ignore ttm column!
            # check if statement available and get id
            ped = dt.datetime.strptime(str(t), '%m/%d/%Y')  # period end date
            sys.path.append(r'C:\Users\MichaelSchwarz\PycharmProjects\FinanceProjects')
            import MyFuncGeneral as My
            cnx = My.cnx_mysqldb('fuyu_jibengong')
            cursor = cnx.cursor()
            cursor.callproc('fuyu_jibengong.usp_py_get_statement_id', ['yahoo', My.date2mysqldatestring(ped), symbol])
            cnx.commit()
            statement_id = [r.fetchall() for r in cursor.stored_results()][0][0][0]

        for (columnName, columnData) in updi.iteritems():
            if np.isnan(columnData.values) == False:
                # check what is the std_item id of the yahoo fundamental item
                q_check_std_id = "select std_item_id from fuyu_jibengong.std_items where fk_datasource = 'yahoo' and std_item_name = '" + columnName + "'"
                std_id = pd.read_sql(q_check_std_id, cnx)
                if std_id.empty:
                    if addLackingFK:
                        print("try to add lacking FK")
                        try:
                            q_addFK = "insert into fuyu_jibengong.std_items(std_item_name,fk_datasource) values ('" + columnName + "' , 'yahoo' )"
                            cursor.execute(q_addFK)
                            cnx.commit()
                            # get created id
                            std_id = pd.read_sql('SELECT LAST_INSERT_ID()', cnx)
                        except:
                            print("something went wrong adding new std_item: " + columnName)
                    else:
                        print("no id found will lead to error: Activate addLackingFK to insert new item names")
                # add the new data item
                query = ("replace into std_fundamentals(fk_statement,fk_std_item,std_value) values (" +
                         str(statement_id) + ", '" + str(std_id.iloc[0,0]) + "' ," + str(columnData.values[0]) + ")")
                try:
                    cursor.execute(query)
                    cnx.commit()
                    print("successfully added/updated stmt_id " + str(statement_id) + ''", '" + columnName + "' , " +
                          str(columnData.values[0]))
                except:
                    print("Not added, probably FK fails for:" + str(statement_id) + ''", '" + columnName + "' , " + str(
                        columnData.values[0]))

        cnx.close()


if __name__ == '__main__':
    symbol = 'ALB'
    # df = scrape(symbol)
    # df.transpose()
    update_db(symbol,True)
