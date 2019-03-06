# AdvNum19_DataServer
First Project

-------------



# Dataserver Project Description

**Elisa FLeissner** &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp;elisa.fleissner@student.unisg.ch <br>
**Lars Stauffenegger** &nbsp; &nbsp; &nbsp;lars.stauffenegger@student.unisg.ch  <br>
**Peter la Cour** &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; peter.lacour@student.unisg.ch

## Overview


* <div id="A1"> <a href="#A2">Setting up the Server </a></div>
* <div id="B1"> <a href="#B2">Installing Firefox on Linux </a></div>
* <div id="C1"> <a href="#C2">The Newspaper Scrape </a></div>
* <div id="D1"> <a href="#D2">Loading the script and Setting up the Cron Job </a></div>
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

The below command creates the table that stores all EOD price data we are fetching from quandl.

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



## <div id="B2"> <a href="#B1">Installing Firefox on Linux</a> </div>

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


## <div id="C2"> <a href="#C1">The Newspaper Scrape</a> </div>

* ( What packages are used )
* ( How does the scrape work )
* 
* 
* Description of scraped data




## <div id="D2"> <a href="#D1">Loading the script and Setting up the Cron Job</a> </div>


* importing the script from local machine
* 
* Script writes to news.db on server.. etc.
* 
* Description of Cron Job Setup ( how it was set up when does it execute )

To automatically run the script each day we set up a cronjob on the server using the commandline code:

```
[user.name]@[server]:/home/advnum$ crontab -e
```

Which opens a crontab editor where we specify the time of the day when we want to execute the script:

```
GNU nano 2.5.3        File: /tmp/crontab.SR97hv/crontab                       

XX XX * * * /home/advnum/top_stories_wsj_ft.py
# Edit this file to introduce tasks to be run by cron.
```

This ...
