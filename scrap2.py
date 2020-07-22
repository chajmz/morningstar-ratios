import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import pandas as pd
import time
import re

URL = 'http://financials.morningstar.com/ratios/r.html?t=AMD'
URL4 = 'http://financials.morningstar.com/ratios/r.html?t=AMDEEEE'
URL2 = "http://financials.morningstar.com/ratios/r.html?t=AAPL"
URL3 = "http://financials.morningstar.com/ratios/r.html?t=GOOGL"

start_col = ["Revenue","Gross Margin %","Operating Income","Operating Margin %",
            "Net Income","Earnings per Share","Dividends","Payout Ratio","Shares","Book Value Per Share",
            "Operating Cash Flow","Cap Spending","Free Cash Flow","Free Cash Flow Per Share","Working Capital"]

cash_name = ["Operating Cash Flow Growth % \YOY","Free Cash Flow Growth % \YOY",
            "Cap Ex as a % \of Sales","Free Cash Flow/Sales %","Free Cash Flow/Sales %"]

efficiency_name = ['Days Sales Outstanding',"Days Inventory","Payables Period",
                    "Cash Conversion Cycle","Receivables Turnover","Inventory Turnover","Fixed Assets Turnover",'Asset Turnover']


growth_name = ["Revenue %","Revenue % | Year Over Year","Revenue % | 3Y Average","Revenue % | 5Y Average","Revenue % | 10Y Average",
                "Operating Income %","Operating Income % | Year Over Year","Operating Income % | 3Y Average","Operating Income % | 5Y Average","Operating Income % | 10Y Average",
                "Net Income %","Net Income % | Year Over Year","Net Income % | 3Y Average","Net Income % | 5Y Average","Net Income % | 10Y Average",
                "EPS %", "EPS % | Year Over Year","EPS % | 3Y Average","EPS % | 5Y Average","EPS % | 10Y Average"]

profitability_name = ["Margins % \of Sales | Revenue","Margins % \of Sales | COGS","Margins % \of Sales | Gross Margin","Margins % \of Sales | SG&A","Margins % \of Sales | R&D","Margins % \of Sales | Other","Operating Margin",
                    "Margins % \of Sales | Net Int Inc & Other","Margins % \of Sales | EBT Margin","Profitability",
                "Profitability | Tax Rate %","Profitability | Net Margin %","Profitability | Asset Turnover (Average)","Profitability | Return on Assets %",
                "Profitability | Financial Leverage (Average)","Profitability | Return on Equity %","Profitability | Return on Invested Capital %",
                "Profitability | Interest Coverage"]
health_name = ["Cash & Short Term Investments","Accounts Receivable","Inventory","Other Current Assets",
                "Total Current Assets","Net PP&E","Intangibles","Other Long-Term Assets","Total Assets",
                "Accounts Payable","Short Term Debt","Taxes Payables","Accrued Liabilities",
                "Other Short Term Liabilities","Total Current Liabilities","Long-Term Debt",
                "Other Long-Term Liabilities","Total Liabilities","Total Stockholders' Equity",
            "Total Liabilities & Equity"," Liquidity/Financial Health","Current Ratio","Quick Ratio",
            "Financial Leverage","Debt/Equity"]

         
         
def get_eda():
    eda = pd.read_csv('eda.csv',sep=";")
    return eda         
                
def main(symbol,name_stock,i):

    def get_year(str_year = "year"):
        return [str_year,"2010-12","2011-12","2012-12","2013-12",
                "2014-12","2015-12","2016-12",
                "2017-12","2018-12","2019-12","TTM"]

    def new_list(old_list):
        new_col = [""]
        for item in old_list:
            new_col.append("")
            new_col.append(item)
        return new_col

    def get_content(content,regex_expr,name):
        col_names = [name]
        for item in content:
            lines = str(item)
            name = re.search(regex_expr, lines)
            if name:
                try:
                    if name.group(3):
                        col_names.append(name.group(3))
                    else:
                        col_names.append(name.group(1))
                except:
                    col_names.append(name.group(1))
        return col_names


    def fin(content,starter):
        reg = r"(?:(?<=i[0-9][0-9]\">)(.*?)(?=(<\/td>))|(?<=i[0-9]\">)(.*?)(?=(<\/td>)))"
        col_names = [starter]
        for item in content:
            lines = str(item)
            name = re.search(reg, lines)
            if name:
                try:
                    if name.group(1):
                        col_names.append(name.group(1))
                    else:
                        col_names.append(name.group(3))
                except:
                    print("Error with name")
                    print(name.group)
                    print(lines)
        return col_names

    def get_financial_section():
        end_list = []
        results = soup.find(id='financeWrap')
        res2 = results.findAll('tr')
        for i in range(2,31,2):
            end_list.append(fin(res2[i],new_list(start_col)[i]))
        df = pd.DataFrame(end_list, columns = get_year())
        df['Section'] = "Financial"
        return df

    def get_subtab(tab,list_name,str_year):
        reg = r"(?:(?<=i[0-9][0-9]\">)(.*?)(?=(<\/td>))|(?<=i[0-9]\">)(.*?)(?=(<\/td>)))"
        results = soup.find(id=tab)
        res2 = results.findAll('tr')
        get_year(str_year)
        for i in range(2,len(res2)-1,2):
            print(get_content(res2[i].contents, reg,new_list(list_name)[i]))
    
        print("\n")

    def get_subtab(start,tab,list_name,str_year):
        end_list = []
        reg = r"(?:(?<=i[0-9][0-9]\">)(.*?)(?=(<\/td>))|(?<=i[0-9]\">)(.*?)(?=(<\/td>)))"
        results = soup.find(id=tab)
        res2 = results.findAll('tr')
        get_year(str_year)
        for i in range(start,len(res2)-1,2):
            end_list.append(get_content(res2[i].contents, reg,new_list(list_name)[i]))
        return end_list
        print("\n")
    

    def create_df(start,tab,list_name,str_year):
        df_to_list = get_subtab(start,tab,list_name,str_year)
        df = pd.DataFrame(df_to_list, columns = get_year())
        df['Section'] = str_year
        return df

    def clean_df(x):
        if x != None:
            if x == "—":
                print(x)
                return x.replace("—","AAA")    

    def get_df_stock(name_stock,symbol):
        df_financial = get_financial_section()
        df_profitability = create_df(0,"tab-profitability", profitability_name,"Profitability")
        df_cashflow = create_df(2,"tab-cashflow",cash_name,"Cash Flow")
        df_efficiency = create_df(2,"tab-efficiency",efficiency_name,"Efficiency")
        df_fhealth = create_df(0,"tab-financial",health_name,"Financial Health")
        df_growth = create_df(2,"tab-growth",growth_name,"Growth")
        list_df = [df_financial,df_profitability,df_cashflow,df_efficiency,df_fhealth,df_growth]
        df_tot = pd.concat(list_df)
        df_tot['name_stock'] = name_stock
        df_tot['symbol'] = symbol
        df_tot = df_tot.replace(to_replace = "—", value ="") 
        df_tot = df_tot.dropna()
        return df_tot.reset_index(drop=True)
    
    def setup_session(symbol, name_stock,i):
        url_symbol = "http://financials.morningstar.com/ratios/r.html?t=" + symbol                
        driver = webdriver.Chrome()
        driver.get(url_symbol)
        html = driver.page_source
        soup = BeautifulSoup(html,features="lxml")
        wait = WebDriverWait(driver, 10)
        try:
            wait.until(EC.title_contains('Page Not '))
            print("Error : {} stock with symbol {} does not exist in Morningstar.".format(name_stock,symbol))
            driver.quit()
            return soup,driver,html,0
        except TimeoutException:
            print("Starting Extraction {} of {} with symbol {}".format(i,name_stock,symbol))                                
        return soup,driver,html,1
    
    
    soup,driver,html,work_bool = setup_session(symbol,name_stock,i)
    
    if work_bool:
        driver.quit()
        return get_df_stock(name_stock,symbol)
       
    driver.close()
    exit()

df_eda = get_eda()
newL2 = []

for i in range(300):
    name_stock = df_eda.iloc[i]['Name']
    symbol = df_eda.iloc[i]['Symbol']
    try:
        df = main(symbol,name_stock,i)
        newL2.append(df)
    except:
        pass

df_fus = pd.concat(newL2).reset_index(drop=True)
df_fus.to_csv("df1_1290_1.csv")

