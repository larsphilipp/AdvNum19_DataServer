
## Title:        Yahoo Finance News Scrape
## Author:       Elisa FLeissner, Lars Stauffenegger, Peter la Cour
## Email:        elisa.fleissner@student.unisg.ch,
##               lars.stauffenegger@student.unisg.ch,
##               peter.lacour@student.unisg.ch
## Place, Time:  St. Gallen, 07.03.19
## Description:  Gets all the news of the specified companies in the Underlyings
##               database from Yahoo Finance and adds it to the TickerNews database
## Improvements: specify timezone and check speed of adding one big dataframe to the database
## Last changes: Included a check for news duplicates

#-----------------------------------------------------------------------------#
# Loading Packages
#-----------------------------------------------------------------------------#
from    DatabaseConnection  import *
from    bs4                 import BeautifulSoup    as bs
import  pandas              as pd
import  numpy               as np
import  requests
import  pymysql
import  datetime

#-----------------------------------------------------------------------------#
# Functions
#-----------------------------------------------------------------------------#

def get_news_of_company( ticker, currentTime, todaysDate, yesterdaysDate ):
    '''
    Description:         Gets all the news from Yahoo Finance for the company with the specified ticker symbol
    Inputs:              Ticker symbol of company, current time when the script is running, today's date and yesterday's date
    Outputs:             DataFrame with all the news headlines, descriptions, links, dates, relative timestamps, types (Videos or Articles)
                         and newspapers of the given company from Yahoo Finance
    '''
    # Get the url with the ticker
    url                  = "https://finance.yahoo.com/quote/" + ticker + "/news?p=" + ticker
    response             = requests.get( url )
    soup                 = bs( response.content, "html.parser" )

    # Get all the newspaper headlines into a list
    headers              = [ k.text for k in soup.find_all('h3') ]

    # Get all the newspaper descriptions into a list
    descriptions         = [ k.find_next('p').text for k in soup.find_all('h3') ]

    # Get all the news links on yahoo finance into a list
    links                = [ 'www.finance.yahoo.com/' + k.find_next('a').get('href') for k in soup.find_all('h3') ]

    # Get all the names of the newspaper that published the articles into a list
    newspaper            = [ k.find_next('span').text for k in soup.find_all( class_ = 'C(#959595)' ) if k.find_next('h3').text in headers ]

    # Get relative time when articles were published
    timestamp            = [ k.find_next('span').find_next('span').text for k in soup.find_all( class_ = 'C(#959595)' ) if k.find_next('h3').text in headers ]

    # Estimate the time of day in decimals when the article was published, i.e. 10:30 => 10.5 or 17:45 => 17.75
    for k in range(len(timestamp)):
        if "minutes" in timestamp[k]:
            timestamp[k] = round( currentTime - float( timestamp[k].replace( " minutes ago", "" ) ) / 60, 2 )
        elif "hours" in timestamp[k]:
            timestamp[k] = round( currentTime - float( timestamp[k].replace( " hours ago", "" ) ) )
        elif "hour" in timestamp[k]:
            timestamp[k] = round( currentTime - float( timestamp[k].replace( " hour ago", "" ) ) )
        elif "yesterday" in timestamp[k]:
            timestamp[k] = round( currentTime - 24.0 )
        else:
            timestamp[k] = np.nan

    # Get the types of news into a list (Video or Article) based on the news tag on Yahoo Finance
    types                = []
    for k in range(len(newspaper)):
        if "Videos" in newspaper[k]:
            types.append("Video")
        else:
            types.append("Article")

    # Generalise the newspaper names by removing " Videos"
    newspaper            = [ k.replace(" Videos","") for k in newspaper ]

    # Create Dictionary containing the data
    data = { "Ticker": ticker, "Date": today, "Headline": headers, "Link": links, "Description": descriptions, "Newspaper": newspaper, "Type": types, "Time": timestamp }

    # Delete duplicate news on yahoo finance from dictionary lists
    for k in headers:
         if headers.count(k) > 1:
            index = headers.index(k)
            for l in ["Headline", "Link", "Description", "Newspaper", "Type", "Time"]:
                data[l].pop( index )

    # Create output DataFrame with dictionary of the scraped data
    output               = pd.DataFrame( data )

    # Check for news duplicates from yesterday's news and remove them from the output dataframe
    yesterdayNews        = db._getYesterdaysNews( ticker, yesterdaysDate )
    output               = output[ output[[ "Ticker", "Headline", "Newspaper" ]].apply( lambda x: x.values.tolist() not in yesterdayNews[[ "Ticker", "Headline", "Newspaper" ]].values.tolist(), axis=1 ) ]

    return output

#-----------------------------------------------------------------------------#
# Body
#-----------------------------------------------------------------------------#

# DB Connection (includes loading of relevant data)
db = DBConn()

# Get current time in decimal format, i.e. 10:30 => 10.5 or 17:45 => 17.75 and today's and yesterday's date
time                     = round( datetime.datetime.now().hour + datetime.datetime.now().minute / 60, 2 )
today                    = datetime.datetime.today().strftime('%Y-%m-%d')
yesterday                = ( datetime.datetime.today() - datetime.timedelta(days = 1) ).strftime('%Y-%m-%d')

# Loop through ticker list to get news data from Yahoo Finance and insert into database
for ticker in db.tickerObject:
    db._insertNews( get_news_of_company( ticker['Ticker'], time, today, yesterday ) )

# Close database connection
db.CloseConn()
