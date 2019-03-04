import quandl
import pandas as pd
import sys
import os
import getpass

username = getpass.getuser()

# write every print statement to txt file
sys.stdout = open("file.txt", "w")

# insert quandl api key
quandl.ApiConfig.api_key = "mrMTRoAdPycJSyzyjxPN"

# specify tickers and database and prepare an empty dataframe
ticker = ["AAPL", "MSFT"]
database = "EOD"
todays_prices = pd.DataFrame()

# for loop to obtain financial data for each ticker
for i in ticker:
    db = database + "/" + i
    mydata = quandl.get(db, rows = 1)
    todays_prices = pd.concat([todays_prices, mydata.Close], axis = 1)

# rename columns
todays_prices.columns = [ticker]

# print results
print (todays_prices)

# close txt file
sys.stdout.close()
