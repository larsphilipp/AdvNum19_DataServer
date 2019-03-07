# AdvNum19_DataServer
First Project

-------------



# Dataserver Project Description

**Elisa FLeissner** &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp;elisa.fleissner@student.unisg.ch <br>
**Lars Stauffenegger** &nbsp; &nbsp; &nbsp;lars.stauffenegger@student.unisg.ch  <br>
**Peter la Cour** &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; peter.lacour@student.unisg.ch

## Overview


* <div id="A1"> <a href="#A2">Setting up the Server </a></div>
* <div id="B1"> <a href="#B2">Create Database in MySQL</a></div>
* <div id="C1"> <a href="#C2">Getting Price Data from Quandl </a></div>
* <div id="D1"> <a href="#D2">Yahoo Finance News Scrape </a></div>
* <div id="E1"> <a href="#E2">Setting up the Cronjobs </a></div>
* (Setting up GitHub?)

## <div id="A1"> <a href="#A2">Setting up the Server  </a> </div>


* Initial Setup
* Setting up users 
* Granting Permissions
* Installing Python
* Installing MySql
* Installing Firefox
* etc.

## <div id="B2"> <a href="#B1">Create Database in MySQL</a> </div>

The type of data that we will request is stored in the following table:

```
CREATE TABLE RequestData (
DataType VARCHAR(20),
Description CHAR(30),
Source VARCHAR(20),
PRIMARY KEY (DataType, Source)
);

INSERT INTO RequestData VALUES ("EOD", "EOD Prices", "Quandl");
```

The underlyings we aim to get data for are defined here:

```
CREATE TABLE Underlyings (
Ticker VARCHAR(10),
Name VARCHAR(20),
PRIMARY KEY (Ticker)
);

INSERT INTO Underlyings VALUES ("AAPL", "APPLE"), ("MSFT", "Microsoft");
```

The below command creates the table that stores all EOD price data we are fetching from Quandl.

```
CREATE TABLE Prices (
Date DATE NOT NULL,
Ticker VARCHAR(10),
Open DECIMAL(14,4),
High DECIMAL(14,4),
Low DECIMAL(14,4),
Close DECIMAL(14,4),
Volume INT,
Dividend DECIMAL(14,4),
Split DECIMAL(14,4),
Adj_Open DECIMAL(14,4),
Adj_High DECIMAL(14,4),
Adj_Low DECIMAL(14,4),
Adj_Close DECIMAL(14,4),
Adj_Volume INT,
PRIMARY KEY (Date, Ticker),
FOREIGN KEY (Ticker) REFERENCES Underlyings(Ticker)
);
```

Furthermore, the command below creates the table that stores all news data that we download from Yahoo Finance.

```
CREATE TABLE TickerNews (
Date DATE NOT NULL,
Ticker VARCHAR(10),
Headline CHAR(255),
Description VARCHAR(4000),
Newspaper CHAR(255),
Link CHAR(255),
Type CHAR(20),
PRIMARY KEY (Date, Ticker, Headline, Newspaper),
FOREIGN KEY (Ticker) REFERENCES Underlyings(Ticker)
);
```



--> Description of Foreign Key, Primary Key, Underlyings Reference



## <div id="C2"> <a href="#C1">Getting Price Data from Quandl</a> </div>






## <div id="D2"> <a href="#D1">Yahoo Finance News Scrape</a> </div>

To get all the news headlines of the given companies we simply used the `Requests` and `Beautiful Soup` webscraping package along with the common `Pandas` and `Numpy` packages to get all the news using the companies ticker symbols saved in our `Underlyings` database. To write the data to the MySQL database we used `sqlalchemy` and `pymysql`.

```python
import requests
from bs4 import BeautifulSoup as bs
import pandas as pd
import numpy  as np
from sqlalchemy import create_engine
import pymysql
import datetime
```


The code that gets the headlines, descriptions, links and the name of the newspapers that published the articles of a given company from Yahoo Finance is written as the `get_news_of_company` function using the `ticker` symbol as the input:

```python
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
```


After loading the database, selecting the tickers from the `Underlyings` database and creating the dataframe that is to be written to the `TickerNews` database we loop through the ticker list, append the data to the dataframe and finally update the dataframe to the TickerNews database using `.tosql`.

```python
# Loading database
engine = db.create_engine('mysql+pymysql://root:advnum19@localhost/dataserver')
connectionObject = engine.connect()

# Getting Ticker's from Underlying
selectTickersQuery      = "select Ticker from Underlyings"
ticker_list =  connectionObject.execute(selectTickersQuery)

# Creating DataFrame
columns = [ "Ticker", "Date", "Headline", "Link", "Description", "Newspaper", "Type" ]
news_df = pd.DataFrame( columns = columns)

# Loop through the ticker list
for ticker in ticker_list:
    news_df = news_df.append(get_news_of_company(ticker['Ticker']), ignore_index = True, sort = False)

# Writing news_df DataFrame to database
news_df.to_sql(name = "TickerNews", con = engine, if_exists='append', index = False)

# CLosing database connection
connectionObject.close()

```


* Description of scraped data ?

![alt text](https://github.com/larsphilipp/AdvNum19_DataServer/tree/master/Screenshots icon48.png "Logo Title Text 1")



## <div id="E2"> <a href="#E1">Loading the script and Setting up the Cron Job</a> </div>


To automatically run the script each day we set up a cronjob on the server using the commandline code:

```
[user.name]@[server]:/home/advnum$ crontab -e
```

Which opens a crontab editor where we specify the time of the day (2:00 AM every day) when we want to execute the two scripts to download the prices from Quandl and the news from Yahoo Finance:

```
GNU nano 2.5.3        File: /tmp/crontab.SR97hv/crontab                       

0 2 * * * /usr/bin/python3 /home/advnum/EODQuandl.py
0 2 * * * /usr/bin/python3 /home/advnum/yahoo_finance_news.py

# Edit this file to introduce tasks to be run by cron.
...
...
```

This will automatically populate our database which in the future we could potentially use to analyse the impact of news on stock prices using a sentiment analysis.





## <div id="Z2"> <a href="#Z1">Installing Firefox on Linux</a> </div>

To install Firefox on Linux we first add its repository with the command:

```
sudo add-apt-repository ppa:mozillateam/firefox-next
```

Before continuing we update the packages on our server to ensure that the new firefox is compatible:

```
sudo apt-get update
```

Finally, we run the following command to install Firefox:

```
sudo apt-get install firefox
```

However, to use the Firefox webdriver for the Python script we need to add its webdriver `geckodriver`. The webdriver can be downloaded here: https://github.com/mozilla/geckodriver/releases. 
To add geckodriver to the server use  

```
scp [/local/filepath/geckodriver] [user.name]@[serverIP]:/home/advnum
```

to secure copy the file from a local machine to the desired directory on the server.
