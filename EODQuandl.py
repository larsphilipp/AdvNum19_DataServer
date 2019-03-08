## Get Quandl Prices
# Packages
import quandl
import os

## Environmental Variable
os.environ["source"] = "Quandl"

## DB Connection (includes loading of relevant data)
db = DBConn()

# Quandl Authentication
quandl.ApiConfig.api_key = db.apiKeyObject

# Fetch Prices and Insert to DB
for ticker in db.tickerObject:
	id = ticker["Ticker"]
	quandlData = quandl.get(db.quandlDataTypeObject + "/" + id, rows = 1)
	date = quandlData.index[0].date().strftime('%Y-%m-%d')
	db.cursorObject.execute("INSERT IGNORE INTO Prices (Date, Ticker, Open, High, Low, Close, Volume, Dividend, Split, Adj_Open, Adj_High, Adj_Low, Adj_Close, Adj_Volume) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",(date, id, float(quandlData.Open[0]), float(quandlData.High[0]), float(quandlData.Low[0]), float(quandlData.Close[0]), float(quandlData.Volume[0]), float(quandlData.Dividend[0]), float(quandlData.Split[0]), float(quandlData.Adj_Open[0]), float(quandlData.Adj_High[0]), float(quandlData.Adj_Low[0]), float(quandlData.Adj_Close[0]), float(quandlData.Adj_Volume[0])))
	db.connectionObject.commit()

db.CloseConn()

