## Title:        EOD Prices Quandl
## Author:       Elisa FLeissner, Lars Stauffenegger, Peter la Cour
## Email:        elisa.fleissner@student.unisg.ch,
##               lars.stauffenegger@student.unisg.ch,
##               peter.lacour@student.unisg.ch
## Place, Time:  Zürich, 08.03.19
## Description:  Gets all the news of the specified companies in the Underlyings
##               database from Quandl and adds it to the Price Table
## Improvements: -
## Last changes: -

#-----------------------------------------------------------------------------#
# Loading Packages
import quandl

## DB Connection (includes loading of relevant data)
db = DBConn()

# Quandl Authentication
quandl.ApiConfig.api_key = db.apiKeyObject

# Fetch Prices and Insert to DB
for ticker in db.tickerObject:
    db._insertQuandlPrices(ticker["Ticker"], quandl.get(db._getDataType("Quandl") + "/" + ticker["Ticker"], rows = 1))

db.CloseConn()




## Title:        Database Connection
## Author:       Elisa FLeissner, Lars Stauffenegger, Peter la Cour
## Email:        elisa.fleissner@student.unisg.ch,
##               lars.stauffenegger@student.unisg.ch,
##               peter.lacour@student.unisg.ch
## Place, Time:  Zürich, 08.03.19
## Description:  Class that handles all data base communication.
##               Different Methods under one instance.
## Improvements: -
## Last changes: -

#-----------------------------------------------------------------------------#
# Loading Packages
import pymysql

## Class as Instance of a Requests Session
class DBConn():
    
    def __init__(self):
        dbServerName    = "localhost"
        self.dbUser     = "root"
        dbPassword      = "advnum19"
        self.dbName     = "dataserver"
        charSet         = "utf8mb4"
        cursorType      = pymysql.cursors.DictCursor
        
        # Cursor
        self.connectionObject = pymysql.connect(host=dbServerName, user=self.dbUser, password=dbPassword, db=self.dbName, charset=charSet,cursorclass=cursorType)
        self.cursorObject = self.connectionObject.cursor()
        
        # Load Data
        self.tickerObject = self._getTickers()
        self.apiKeyObject = self._getAPIKey()
        
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
    
    def CloseConn(self):
        # Close the database connection
        self.connectionObject.close()

