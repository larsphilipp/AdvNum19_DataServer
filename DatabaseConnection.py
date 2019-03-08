## DB Connection

## Import Packages
import pymysql
import os

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
        self.quandlDataTypeObject = self._getQuandlDataType()
        self.apiKeyObject = self._getAPIKey()
        
    def _getTickers(self):
        self.cursorObject.execute("select Ticker from Underlyings")
        return self.cursorObject.fetchall()
    
    def _getQuandlDataType(self):
        self.cursorObject.execute("select DataType from RequestData where Source = '{}' ".format(os.environ.get('source', None)))
        return self.cursorObject.fetchall()[0]["DataType"]
    
    def _getAPIKey(self):
        self.cursorObject.execute("select APIKey from Authentications where User = '{}' ".format(self.dbUser))
        return self.cursorObject.fetchall()[0]["APIKey"]
    
    def CloseConn(self):
        # Close the database connection
        self.connectionObject.close()
