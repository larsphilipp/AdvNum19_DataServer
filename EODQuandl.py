#!/bin/python3

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
from    DatabaseConnection import *
import  quandl

## DB Connection (includes loading of relevant data)
db = DBConn()

# Quandl Authentication
quandl.ApiConfig.api_key = db.apiKeyObject

# Fetch Prices and Insert to DB
for ticker in db.tickerObject:
    db._insertQuandlPrices(ticker["Ticker"], quandl.get(db._getDataType("Quandl") + "/" + ticker["Ticker"], rows = 1))

db.CloseConn()
