<div align="right">
Advanced Numerical Methods and Data Analysis - FS19-8,780
<br>
University of St. Gallen, 10.03.2019
<br>
</div>

-------------



# Dataserver Project Description

**Elisa Fleissner** &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp;  elisa.fleissner@student.unisg.ch <br>
**Lars Stauffenegger** &nbsp; &nbsp; &nbsp;lars.stauffenegger@student.unisg.ch  <br>
**Peter la Cour** &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; peter.lacour@student.unisg.ch

## <div id="0">Overview</div>

1. <a href="#2">Introduction</a>
2. <a href="#A2">Setting up the Linux Server</a>
3. <a href="#B2">Setting up the MySQL Database</a>
4. <a href="#X2">Setting up the Database Connection to the Python Scripts</a>
5. <a href="#C2">Getting Price Data from Quandl</a>
6. <a href="#D2">Getting News Data from Yahoo Finance</a>
7. <a href="#E2">Setting up the Cronjobs </a>
8. <a href="#F2">Concluding Remarks</a>


## <div id="2"> <a href="#0">Introduction  </a> </div>

This is the documentation for the first assignment of the class **Advanced Numerical Methods and Data Analysis** taught by Prof. Peter Gruber at the University of St. Gallen in Spring 2019. We - Elisa Fleissner, Lars Stauffenegger and Peter La Cour - are in the 2nd Semester of our Master studies and worked as a group with the aim to set up an automated financial data mining application. Our goal is to collect price and news data of 29 Large Cap US Equities on a daily basis and store them on a data server. For the price data we use Quandl's API (www.quandl.com) whilst the headlines are scraped from [Yahoo Finance](https://finance.yahoo.com/).

### Project plan ###
After a short brainstorming session we decided to scrape financial data as we were already aware of available sources. Given the time horizon of roughly 2.5 weeks we immediately assigned independent tasks. Elisa took over the Quandl mining, Peter wrote the headline scraping script and Lars did set up the server and the MySQL tables and connections.

### Ressources ###
We rented a VPS with Ubuntu 16.04 Server (64-bit version), 2 vCore, ~2GHz, 4 GB RAM, 50 GB at www.ovh.com. The main tools we used are MySQL 5.7.25 for Ubuntu and Python 3.5.2. All missing Python packages were installed using `pip3 install`.

<div align="right"><a href="#0">Back to top</a> </div>

## <div id="A2"> <a href="#0">Setting up the Linux Server</a> </div>

The server itself needs little setup work. Most importantly the root user creates individual users and adds them to the group.

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

<div align="right"><a href="#0">Back to top</a> </div>

## <div id="B2"> <a href="#0">Setting up the MySQL Database</a> </div>

### MySQL Setup ###

Once the server is ready and accessible for all users, a MySQL database is installed and the root user starts the application in order to set a password.

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


### Create tables ###

The database is used to store in- and output values of the python codes. It consists of three input tables (RequestData, Underlyings, Authentications) and two output tables (Prices, News).

The use of `PRIMARY KEY` and `FOREIGN KEY` ensures that we will not have duplicate entries and that we will use the same tickers we entered in the `Underlyings` table in both applications (get prices and get headlines). `PRIMARY KEY` allows to specify which column per entry shall be unique, and it is also possible to specify combinations that need to be unique, such as the combination of Date and Ticker in the `Prices` table. This means that every ticker can only have one entry per date and in the case of a multiple download on one day, an error would be raised. 

The `FOREIGN KEY` refers to a `PRIMARY KEY` in the table specified through the `REFERENCE` statement and prevents invalid entries and thus protects the linkage between the different tables. We use a `FOREIGN KEY` in the output tables (Prices, News) to make sure, that the ticker in these tables are the same as they are in the `Underlyings` table.

The type of data that we will request is stored in the following table together with a desciption and the name of the data source. A combination of Source and DataType can only occur once.

```
CREATE TABLE RequestData (
DataType VARCHAR(20),
Description CHAR(30),
Source VARCHAR(20),
PRIMARY KEY (DataType, Source)
);
```

The underlyings we aim to get data for are defined here. A ticker can only occur once and will be used in output tables as foreign key.

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

The below table is created to store all End-of-Day price data we are fetching from Quandl. The columns represent all fields delivered from Quandl when requesting EOD Prices. 

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

Furthermore, the command below creates the table that stores all news data that we downloaded from Yahoo Finance.

```
CREATE TABLE News (
Date DATE NOT NULL,
Ticker VARCHAR(10),
Headline CHAR(255) CHARACTER SET utf8,
Description VARCHAR(16383) CHARACTER SET utf8,
Newspaper CHAR(255),
Link CHAR(255),
Type CHAR(20),
Time VARCHAR(10),
PRIMARY KEY (Date, Ticker, Headline, Newspaper),
FOREIGN KEY (Ticker) REFERENCES Underlyings(Ticker)
);
```

### Tables structure
Below we drew an Entity-Relationship-Model for our data structure within the MySQL database.

<img src="Screenshots/EntityRelationshipModel.png"
     alt="Screenshot of EP Model"
     style="float: left; margin-right: 10px; padding-bottom: 30px;" />

<div align="right"><a href="#0">Back to top</a> </div>

## <div id="X2"> <a href="#0">Setting up the Database Connection to the Python Scripts</a> </div>

To easily read data from the MySQL database into our Python scripts, we created an object class in a separate Python file called `DatabaseConnection.py`. This file allows us to organise and reuse data base communication logic in an efficient manner for both mining codes.

First, we import the required packages.

```python
import pymysql
import json
import sqlalchemy  as db
```

As the object `DBConn` is called, the following code will directly be executed. The `config.json` file does contain the credentials needed to login to the database. Also, at initiation, the ticker list from the `Underlyings` table and Quandl API key will be loaded directly.
<details><summary>Click to see the code</summary>
<p>
     
```python
class DBConn():
    def __init__(self):

        with open('config.json') as json_file:
            credentials = json.load(json_file)

        dbServerName    = "localhost"
        self.dbUser     = credentials['dataserverDB']['user']
        self.dbPassword = credentials['dataserverDB']['password']
        self.dbName     = "dataserver"
        charSet         = "utf8mb4"
        cursorType      = pymysql.cursors.DictCursor

        # Cursor
        self.connectionObject = pymysql.connect(host=dbServerName, user=self.dbUser, password=self.dbPassword, db=self.dbName, charset=charSet,cursorclass=cursorType)
        self.cursorObject = self.connectionObject.cursor()

        # Load Data
        self.tickerObject = self._getTickers()
        self.apiKeyObject = self._getAPIKey()
```
</details>
</p>
<br>

We then defined several functions to be performed for the object `DBConn`. These functions execute predefined SQL statements and are used to structure and faciliate the database communication in our code. 
<details><summary>Click to see the code</summary>
<p>
     
```python
    def _getTickers(self):
        self.cursorObject.execute("SELECT Ticker FROM Underlyings")
        return self.cursorObject.fetchall()

    def _getDataType(self, source):
        self.cursorObject.execute("SELECT DataType FROM RequestData WHERE Source = '{}' ".format(source))
        return self.cursorObject.fetchall()[0]["DataType"]

    def _getAPIKey(self):
        self.cursorObject.execute("SELECT APIKey FROM Authentications WHERE User = '{}' ".format(self.dbUser))
        return self.cursorObject.fetchall()[0]["APIKey"]

    def _insertQuandlPrices(self, ticker, quandlData):
        date = quandlData.index[0].date().strftime('%Y-%m-%d')
        self.cursorObject.execute("INSERT IGNORE INTO Prices (Date, Ticker, Open, High, Low, Close, Volume, Dividend, Split, Adj_Open, Adj_High, Adj_Low, Adj_Close, Adj_Volume) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",(date, ticker, float(quandlData.Open[0]), float(quandlData.High[0]), float(quandlData.Low[0]), float(quandlData.Close[0]), float(quandlData.Volume[0]), float(quandlData.Dividend[0]), float(quandlData.Split[0]), float(quandlData.Adj_Open[0]), float(quandlData.Adj_High[0]), float(quandlData.Adj_Low[0]), float(quandlData.Adj_Close[0]), float(quandlData.Adj_Volume[0])))
        self.connectionObject.commit()

    def _insertNews(self, news_df):
        self.engine = db.create_engine('mysql+pymysql://{0}:{1}@localhost:3306/dataserver'.format(self.dbUser, self.dbPassword))
        news_df.to_sql(name = "News", con = self.engine, if_exists='append', index = False)

    def _getYesterdaysNews(self, ticker, yesterday):
        self.engine = db.create_engine('mysql+pymysql://{0}:{1}@localhost/dataserver'.format(self.dbUser, self.dbPassword))
        return pd.read_sql("SELECT * FROM News WHERE (Date = '" + yesterday + "') AND (Ticker = '" + ticker + "');", con = self.engine)

    def CloseConn(self):
        # Close the database connection
        self.connectionObject.close()
```
</details>
</p>
<br>

<div align="right"><a href="#0">Back to top</a> </div>

## <div id="C2"> <a href="#0">Getting Price Data from Quandl</a> </div>

### Quandl database ###

The Quandl database has been chosen over Yahoo Finance for the stock price information. This is due to the discontinued support of the API of Yahoo Finance. Quandl is a platform that collects various types of data including economic data such as GDP or sentiment data but also financial data, which we will access for the purpose of this project. For our project we chose the Quandl database `EOD` which collects End of Day US Stock Prices. The publisher of this database is Quotemedia. The database comprises around 8000 stocks, which can be accessed through `EOD/{Ticker}` using the Quandl API. As we did only create a free account, we had access to 29 stocks which we entered into the `Underlyings` table in our database.

### Quandl API ###

Within the `EODQuandl.py` file we first import all relevant data from the `DatabaseConnection.py` file. Further, we import the `quandl` package.

```python
from    DatabaseConnection import *
import  quandl
```

To initiate the database connection class from `DatabaseConnection.py`, we call:

```python
db = DBConn()
```

Then we have to provide the Quandl API Key, which is linked to the account we registered with. As the API key is stored in the `Authentications` table we call this entry to get the required information from the `DBConn` class:

```python
quandl.ApiConfig.api_key = db.apiKeyObject
```

We are now able to download the data from the Quandl database `EOD` with the following `for` loop, which loops over each ticker in the `Underlyings` table. The command below inserts the output of the price download directly into the database using the `._insertQuandlPrices` function from the `DBConn` class. As a last step, we close the connection to the database.

```python
for ticker in db.tickerObject:
    db._insertQuandlPrices(ticker["Ticker"], quandl.get(db._getDataType("Quandl") + "/" + ticker["Ticker"], rows = 1))

db.CloseConn()
```

<img src="Screenshots/QuandlPrices.png"
     alt="Screenshot of Prices database"
     style="float: left; margin-right: 10px; padding-bottom: 30px;" />
<br>

<div align="right"><a href="#0">Back to top</a> </div>

## <div id="D2"> <a href="#0">Getting News Data from Yahoo Finance</a> </div>

The `YahooFinanceNews.py` script was written to get all the news data displayed on yahoo finance for a given company in our `Underlyings` table.

### Yahoo Finance News Scrape ###

To get all the news headlines of the given companies the script uses the `Requests` and `Beautiful Soup` webscraping packages along with the common `Pandas` and `Numpy` packages to download all the news articles using the companies ticker symbols saved in our `Underlyings` table. To ensure we get the correct timestamp and to deal with potential duplicate values we also import the `datetime` package.

<details><summary>Click to see the code</summary>
<p>

```python
from    DatabaseConnection  import *
from    bs4                 import BeautifulSoup    as bs
import  pandas              as pd
import  numpy               as np
import  requests
import  datetime

```
</details>
</p>
<br>

The code that gets the headlines, descriptions, links and the name of the newspapers that published the articles of a given company from Yahoo Finance is written as the `get_news_of_company` function using the `ticker` symbol and today's and yesterday's data as inputs. We use yesterday's date to check if there are still news headlines from the day before on Yahoo Finance to avoid duplicates in our data. 

<details><summary>Click to see the code</summary>
<p>

```python
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
            timestamp[k] = round( currentTime - 24.0, 2 )
        elif "days" in timestamp[k]:
            timestamp[k] = round( currentTime - 24.0 * float(timestamp[k].replace(" days ago", "")) )
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
```

</details>
</p>
<br>

After loading the `DBConn` class, and getting the current time, today's date and yesterday's date, we loop through the ` db.tickerObject` which contains all the tickers from the `Underlyings` table and insert the dataframe output from the `get_news_of_company()` function directly into the `News` database table.


<details><summary>Click to see the code</summary>
<p>

```python
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

```

</details>
</p>
<br>

### Description of the Yahoo Finance News Data ###

The screenshot below shows an excerpt from the `News` table. The *'Headline'* column for example shows all the news headlines shown on the Yahoo Finance summary website for [Apple](https://finance.yahoo.com/quote/AAPL/) on the 10th of March 2019. The *'Newspaper'* column shows the newspapers that published the article and the *'Type'* column specifies whether it is a video or an article.

The *'Time'* column shows the approximated time of when the article was published. The negative values shown in the screenshot indicate that the articles were published on previous days from the scrape date. Once the database populates these numbers should generally range from 0.00 to 24.00.

<img src="Screenshots/YahooFinanceNews.png"
     alt="Screenshot of TickerNews database"
     style="float: left; margin-right: 10px;padding-bottom: 30px;" />

Finally, the last column of the news data is the *'Description'* associated with the headlines on Yahoo Finance. Given the varying length of the article descriptions we only included a screenshot of the *'Description'* column of the first 3 headlines from Apple shown in the screenshot above: 

<img src="Screenshots/YahooFinanceNewsDescriptions.png"
     alt="Screenshot of TickerNews database"
     style="float: left; margin-right: 10px;padding-bottom: 30px;" />

<div align="right"><a href="#0">Back to top</a> </div>

## <div id="E2"><a href="#0">Setting up the Cronjobs </a> </div>


To automatically run the script each day we set up a cronjob on the server using the commandline code:

```
[user.name]@[server]:/home/AdvNum19_DataServer$ crontab -e
```

Which opens a crontab editor where we specify the times when we want to execute the two scripts to download the prices from Quandl and the news from Yahoo Finance:

```
GNU nano 2.5.3        File: /tmp/crontab.SR97hv/crontab                       

30 23 * * 1-5 /usr/bin/python3 /home/AdvNum19_DataServer/EODQuandl.py >"/home/AdvNum19_DataServer/EODQuandlCrontab.log" 2>&1
30 23 * * * /usr/bin/python3 /home/AdvNum19_DataServer/YahooFinanceNews.py >"home/AdvNum19_DataServer/yahooFinanceNewsCrontab.log" 2>&1


# Edit this file to introduce tasks to be run by cron.
...
...
```

This will automatically populate the tables in our database at 23:30 from Monday to Friday with the data from Quandl and Yahoo Finance. In case that there was a problem running the code via the cronjobs, the error code will be written into the log files `EODQuandlCrontab.log` and `YahooFinanceNewsCrontab.log`.
 
<div align="right"><a href="#0">Back to top</a> </div>

## <div id="F2"><a href="#0">Concluding Remarks</a> </div>

The purpose of our project was to create a data server that automatically updates a database consisting of price data from US Large Cap Equities and their associated news.

In the future we could potentially use this data to analyse the impact of news on stock prices using a sentiment analysis of the news headlines. More specifically, we could for example anaylse the over- or underreaction following news over a given time frame or do a volume weigthed analysis based on a news sentiment indicator.



<div align="right"><a href="#0">Back to top</a> </div>
