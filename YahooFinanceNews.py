
## Title:        Yahoo Finance News Scrape
## Author:       Elisa FLeissner, Lars Stauffenegger, Peter la Cour
## Email:        elisa.fleissner@student.unisg.ch,
##               lars.stauffenegger@student.unisg.ch,
##               peter.lacour@student.unisg.ch
## Place, Time:  St. Gallen, 07.03.19
## Description:  Gets all the news of the specified companies in the Underlyings
##               database from Yahoo Finance and adds it to the TickerNews database
## Improvements: -
## Last changes: -

#-----------------------------------------------------------------------------#
# Loading Packages
#-----------------------------------------------------------------------------#
from    bs4         import BeautifulSoup    as bs
from    sqlalchemy  import create_engine
from    sqlalchemy  import update
import  sqlalchemy  as db
import  pandas      as pd
import  numpy       as np
import  requests
import  pymysql
import  datetime


#-----------------------------------------------------------------------------#
# Functions
#-----------------------------------------------------------------------------#

def get_news_of_company( ticker ):
    '''
    Description:   Gets all the news from Yahoo Finance for the company with the specified ticker symbol
    Inputs:        Ticker symbol of company
    Outputs:       DataFrame with all the news headlines, descriptions, links, dates, and types (Videos or Articles)
                   and newspapers of the given company from Yahoo Finance
    '''
    # Get the url with the ticker
    url             = "https://finance.yahoo.com/quote/AAPL/news?p=" + ticker
    response        = requests.get(url)
    soup            = bs(response.content, "html.parser")
    # Get today's date
    today           = datetime.datetime.today().strftime('%Y-%m-%d')
    # Get all the newspaper headlines into a list
    headers         = [ k.text for k in soup.find_all('h3') ]
    # Get all the newspaper descriptions into a list
    descriptions    = [ k.find_next('p').text for k in soup.find_all('h3') ]
    # Get all the news links on yahoo finance into a list
    links           = [ 'www.finance.yahoo.com/' + k.find_next('a').get('href') for k in soup.find_all('h3') ]
    # Get all the newspaper names that published the articles into a list
    newspaper       = [ k.find_next('span').text for k in soup.find_all( class_ = 'C(#959595)') ]
    # Get the types of news into a list (Video or Article) based on the news tag on Yahoo Finance
    types           = []
    for k in range(len(newspaper)):
        if "Videos" in newspaper[k]:
            types.append("Video")
        else:
            types.append("Article")
    # Generalise the newspaper names by removing "Videos"
    newspaper       = [ k.replace(" Videos","") for k in newspaper ]
    # Create dictionary with the scraped data to write to DataFrame
    data            = { "Ticker": ticker, "Date": today, "Headline": headers, "Link": links, "Description": descriptions, "Newspaper": newspaper, "Type": types }
    return pd.DataFrame(data)

#-----------------------------------------------------------------------------#
# Body
#-----------------------------------------------------------------------------#

# Load 'dataserver' database
engine              = db.create_engine('mysql+pymysql://root:advnum19@localhost/dataserver')
connectionObject    = engine.connect()

# Get 'Tickers' from the 'Underlyings' table
selectTickersQuery  = "select Ticker from Underlyings"
ticker_list         =  connectionObject.execute(selectTickersQuery)

# Create 'news_df' DataFrame
columns             = [ "Ticker", "Date", "Headline", "Link", "Description", "Newspaper", "Type" ]
news_df             = pd.DataFrame( columns = columns)

# Loop through ticker list to get news data from Yahoo Finance
for ticker in ticker_list:
    news_df         = news_df.append(get_news_of_company(ticker['Ticker']), ignore_index = True, sort = False)

# Write 'news_df' DataFrame to the 'TickerNews' table in the dataserver database
news_df.to_sql(name = "TickerNews", con = engine, if_exists='append', index = False)

# Close the database connection
connectionObject.close()
