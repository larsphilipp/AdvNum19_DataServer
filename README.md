<div align="right">
Advanced Numerical Methods and Data Analysis - FS19-8,780
<br>
University of St. Gallen, 10.03.2019
<br>
</div>

-------------



# Dataserver Project Description

**Elisa Fleissner** &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; elisa.fleissner@student.unisg.ch <br>
**Lars Stauffenegger** &nbsp; &nbsp; &nbsp;lars.stauffenegger@student.unisg.ch  <br>
**Peter la Cour** &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; peter.lacour@student.unisg.ch

## Overview

1. <div id="1"> <a href="#2">Introduction</a></div>
2. <div id="A1"> <a href="#A2">Setting up the Server </a></div>
3. <div id="B1"> <a href="#B2">Create Database in MySQL</a></div>
4. <div id="C1"> <a href="#C2">Getting Price Data from Quandl </a></div>
5. <div id="D1"> <a href="#D2">Yahoo Finance News Scrape </a></div>
6. <div id="E1"> <a href="#E2">Setting up the Cronjobs </a></div>
7. (Setting up GitHub?)

## <div id="2"> <a href="#1">Introduction  </a> </div>

This is the Documentation for the first Assignment of the class **Advanced Numerical Methods and Data Analysis** thaught by Prof. Peter Gruber at the University of St. Gallen in Spring 2019. We - Elisa Fleissner, Lars Stauffenegger and Peter La Cour - are in the 2nd Semester of our Master studies and worked as a group with the aim to setup up an automated financial data mining application. Our goal is to collect price and news data of 50 Large Cap US Equities on a daily basis and store them on a data server. For the price data we use Quandl's API whilst the headlines are scraped from www.yahoo.com.
### Project Plan ###
After a short brainstorming we decided to scrape financial data as we were already aware of available source. Give the time horizon of roughly 2.5 weeks we immediately assigned independent tasks. Elisa took over the Quandl mining, Peter wrote the 

### Ressources ###
We rented a VPS with Ubuntu 16.04 Server (64-bit version), 2 vCore, ~2GHz, 4 GB RAM, 50 GB at www.ovh.com. The main tools we used are MySQL 5.7.25 for Ubuntu and Python 3.5.2. All missing Python packages wer installed using `pip3 install`.



## <div id="A2"> <a href="#A1">Linux Server  </a> </div>

The server itself needs little setup work. Most importantly the root user creates individual users and add them to the group.
```
adduser abc
groupadd AdvNum1 
usermod -a -G AdvNum1 abc
```
The project is cloned from Github into individual workspaces and - for production - into the home directory, where rights are granted to the group.
```
git clone https://github.com/larsphilipp/AdvNum19_DataServer.git
chgrp AdvNum1 ./AdvNum19_DataServer
chmod g+rwx  ./AdvNum19_DataServer
```

## <div id="B2"> <a href="#B1">MySQL Database</a> </div>

### MySQL Setup ###

Once the server is ready and accessible for all users a MySQL database is installed and the root user starts the application in order to set a password.
```
sudo apt-get install mysql-server
/usr/bin/mysql -u root -p
```
The root user now creates a database named after the project.
```
CREATE DATABASE dataserver;
```
Then personal users are added. 
```
INSERT INTO mysql.user (User,Host,authentication_string,ssl_cipher,x509_issuer,x509_subject) VALUES
('abc','localhost',PASSWORD('secret'),'','','');
FLUSH PRIVILEGES;
```
Rights are granted for the relevant database.
```
GRANT SELECT,INSERT,UPDATE ON dataserver.* TO 'abc'@'localhost';
FLUSH PRIVILEGES;
```


### Create Tables ###

The database is used to store in- and output values of the python codes. It consists of three input tables (RequestData, Underlyings, Authentications) and two output tables (Prices, Headlines).
<br>
The type of data that we will request is stored in the following table together with a desciption and the name of the data source. A combination of Source and DataType can only occur once.

```
CREATE TABLE RequestData (
DataType VARCHAR(20),
Description CHAR(30),
Source VARCHAR(20),
PRIMARY KEY (DataType, Source)
);
```

The underlyings we aim to get data for are defined here. A ticker can only occur once and will be used in output talbes as foreign key.
```
CREATE TABLE Underlyings (
Ticker VARCHAR(10),
Name VARCHAR(20),
PRIMARY KEY (Ticker)
);
```

The authentications table centrally stores APIKeys if needed for web requests. Per source and user only one key can exist in the table.
```
CREATE TABLE Authentications (
User VARCHAR(25),
APIKey VARCHAR(30),
Source VARCHAR(20),
PRIMARY KEY (User, Source)
);
```

The below table is created to stores all End-of-Day price data we are fetching from Quandl. The columns represent all fields delivered from Quandl when requesting EOD Prices. 

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

## collapsible markdown?

<details><summary>Click me</summary>
<p>

#### yes, even hidden code blocks!

```python
print("hello world!")
```

</p>
</details>
<br>

<img src="Screenshots/QuandlPrices.png"
     alt="Screenshot of Prices database"
     style="float: left; margin-right: 10px; padding-bottom: 30px;" />
<br>

## <div id="D2"> <a href="#D1">Yahoo Finance News Scrape</a> </div>

The `YahooFinanceNews.py` script was uploaded from our local machine using the command below.

```
scp [local.file.path]/YahooFinanceNews.py [user.name]@[server.IP]:/home/advnum
```

To get all the news headlines of the given companies the script uses the `Requests` and `Beautiful Soup` webscraping package along with the common `Pandas` and `Numpy` packages to download all the news articles using the companies ticker symbols saved in our `Underlyings` table. To write the data to the MySQL database we use `sqlalchemy` and `pymysql`.

```python
from    bs4         import BeautifulSoup    as bs
from    sqlalchemy  import create_engine
from    sqlalchemy  import update
import  sqlalchemy  as db
import  pandas      as pd
import  numpy       as np
import  requests
import  pymysql
import  datetime

```

The code that gets the headlines, descriptions, links and the name of the newspapers that published the articles of a given company from Yahoo Finance is written as the `get_news_of_company` function using the `ticker` symbol as the input:

```python
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

```


After loading the database, selecting the tickers from the `Underlyings` table and creating the dataframe that is to be written to the `TickerNews` table we loop through the ticker list, append the data to the dataframe and finally update the dataframe to the TickerNews table using `.tosql`.

```python
# Load 'dataserver' database
engine              = db.create_engine('mysql+pymysql://root:advnum19@localhost/dataserver')
connectionObject    = engine.connect()

# Get 'Ticker's from the 'Underlyings' table
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

```


* Description of scraped data ?


<img src="Screenshots/YahooFinanceNews.png"
     alt="Screenshot of TickerNews database"
     style="float: left; margin-right: 10px;padding-bottom: 30px;" />



## <div id="E2"><a href="#E1">Setting up the Cronjobs </a> </div>


To automatically run the script each day we set up a cronjob on the server using the commandline code:

```
[user.name]@[server]:/home/advnum$ crontab -e
```

Which opens a crontab editor where we specify the times when we want to execute the two scripts to download the prices from Quandl and the news from Yahoo Finance:

```
GNU nano 2.5.3        File: /tmp/crontab.SR97hv/crontab                       

30 23 * * 1-5 /usr/bin/python3 /home/advnum/EODQuandl.py
30 23 * * 1-5 /usr/bin/python3 /home/advnum/yahoo_finance_news.py

# Edit this file to introduce tasks to be run by cron.
...
...
```

This will automatically populate the tables in our database at 23:30 from Monday to Friday. In the future we could potentially use this data to analyse the impact of news on stock prices using a sentiment analysis of the news headlines.





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
