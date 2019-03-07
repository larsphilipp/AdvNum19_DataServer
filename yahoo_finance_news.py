
## Title:        Yahoo Finance News Scrape
## Author:       Elisa FLeissner, Lars Stauffenegger, Peter la Cour
## Email:        elisa.fleissner@student.unisg.ch,
##               lars.stauffenegger@student.unisg.ch,
##               peter.lacour@student.unisg.ch
## Place, Time:  St. Gallen, 5.03.19
## Description:
##
## Improvements: -
## Last changes: -

#-----------------------------------------------------------------------------#
# Loading Packages
#-----------------------------------------------------------------------------#

import requests
from bs4 import BeautifulSoup as bs
import pandas as pd
import numpy  as np
from sqlalchemy import create_engine
import pymysql
import datetime
import sqlalchemy as db
from sqlalchemy import update

#-----------------------------------------------------------------------------#
# Functions
#-----------------------------------------------------------------------------#

def get_news_of_company( ticker ):
    '''
    Description:
    Inputs:
    Outputs:
    '''

    url             = "https://finance.yahoo.com/quote/AAPL/news?p=" + ticker
    response        = requests.get(url)
    soup            = bs(response.content, "html.parser")
    today           = datetime.datetime.today().strftime('%Y-%m-%d')
    headers         = [ k.text for k in soup.find_all('h3') ]
    descriptions    = [ k.find_next('p').text for k in soup.find_all('h3') ]
    links           = [ 'www.finance.yahoo.com/' + k.find_next('a').get('href') for k in soup.find_all('h3') ]
    newspaper       = [ k.find_next('span').text for k in soup.find_all( class_ = 'C(#959595)') ]
    types           = []
    for k in range(len(newspaper)):
        if "Videos" in newspaper[k]:
            types.append("Video")
        else:
            types.append("Article")
    newspaper       = [ k.replace(" Videos","") for k in newspaper ]
    data            = { "Ticker": ticker, "Date": today, "Headline": headers, "Link": links, "Description": descriptions, "Newspaper": newspaper, "Type": types }
    return pd.DataFrame(data)

#-----------------------------------------------------------------------------#
# Body
#-----------------------------------------------------------------------------#

# Loading Database
engine = db.create_engine('mysql+pymysql://root:advnum19@localhost/dataserver')
connectionObject = engine.connect()
# Getting Tickers
# ticker_list = [ 'AAPL', 'MSFT']

selectTickersQuery      = "select Ticker from Underlyings"
ticker_list =  connectionObject.execute(selectTickersQuery)


# Creating DataFrame
columns = [ "Ticker", "Date", "Headline", "Link", "Description", "Newspaper", "Type" ]
news_df = pd.DataFrame( columns = columns)
for ticker in ticker_list:
    news_df = news_df.append(get_news_of_company(ticker['Ticker']), ignore_index = True, sort = False)

# Writing DataFrame to database
news_df.to_sql(name = "TickerNews", con = engine, if_exists='append', index = False)

# CLosing database connection
connectionObject.close()

print("Database updated.")
