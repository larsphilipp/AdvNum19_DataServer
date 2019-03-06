## Get Quandl Prices
# Packages
import getpass
import pymysql
import quandl

# Manual Inputs
username = getpass.getuser()
source = "Quandl"
dbServerName    = "localhost"
dbUser          = "root"
dbPassword      = "advnum19"
dbName          = "dataserver"
charSet         = "utf8mb4"
cursorType      = pymysql.cursors.DictCursor

# DB Connection
connectionObject = pymysql.connect(host=dbServerName, user=dbUser, password=dbPassword, db=dbName, charset=charSet,cursorclass=cursorType)
cursorObject = connectionObject.cursor() 

# SQL Queries 
selectTickersQuery = "select Ticker from Underlyings"
selectRequestDataTypeQuery = "select DataType from RequestData where Source = '{}' ".format(source)
selectAPIKeyQuery = "select APIKey from Authentications where User = '{}' ".format(username)

# Get Tickers
cursorObject.execute(selectTickersQuery)
tickersObject = cursorObject.fetchall()

# Get Request Data Type
cursorObject.execute(selectRequestDataTypeQuery)
requestDataTypeObject = cursorObject.fetchall()
requestDataType = requestDataTypeObject[0]["DataType"]

# Get Authentication Key
cursorObject.execute(selectAPIKeyQuery)
quandlApiKeyObject = cursorObject.fetchall()
quandl.ApiConfig.api_key = quandlApiKeyObject[0]["APIKey"] 

# Fetch Prices and Insert to DB
for ticker in tickersObject:
	id = ticker["Ticker"]
	quandlData = quandl.get(requestDataType + "/" + id, rows = 1)
	date = quandlData.index[0].date().strftime('%Y-%m-%d')
	cursorObject.execute("INSERT IGNORE INTO Prices (Date, Ticker, Open, High, Low, Close, Volume, Dividend, Split, Adj_Open, Adj_High, Adj_Low, Adj_Close, Adj_Volume) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",(date, id, float(quandlData.Open[0]), float(quandlData.High[0]), float(quandlData.Low[0]), float(quandlData.Close[0]), float(quandlData.Volume[0]), float(quandlData.Dividend[0]), float(quandlData.Split[0]), float(quandlData.Adj_Open[0]), float(quandlData.Adj_High[0]), float(quandlData.Adj_Low[0]), float(quandlData.Adj_Close[0]), float(quandlData.Adj_Volume[0])))
	connectionObject.commit()