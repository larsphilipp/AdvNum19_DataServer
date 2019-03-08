
## Title:        Cronjob Setup
## Author:       Elisa FLeissner, Lars Stauffenegger, Peter la Cour
## Email:        elisa.fleissner@student.unisg.ch,
##               lars.stauffenegger@student.unisg.ch,
##               peter.lacour@student.unisg.ch
## Place, Time:  St. Gallen, 07.03.19
## Description:  --
##
## Improvements: -
## Last changes: -

#-----------------------------------------------------------------------------#
# Loading Packages
#-----------------------------------------------------------------------------#

from    crontab     import CronTab
from    sqlalchemy  import create_engine
from    sqlalchemy  import update
import  sqlalchemy  as db
# import  pymysql
# from tkinter.ttk import *

# Manual Inputs
username 		= "root"
dbServerName    = "localhost"
dbUser          = "root"
dbPassword      = "advnum19"
dbName          = "dataserver"
charSet         = "utf8mb4"
cursorType      = pymysql.cursors.DictCursor

# DB Connection
connectionObject= pymysql.connect(host=dbServerName, user=dbUser, password=dbPassword, db=dbName, charset=charSet,cursorclass=cursorType)
cursorObject 	= connectionObject.cursor()

# Get crontab and clear all cronjobs
cron 			= CronTab(tabfile='crontab.tab')
cron.remove_all()

# Yahoo cronjob, Time: 23:30 - Monday to Friday
yahooCronJob  	= cron.new(command='/usr/bin/python3 /home/advnum/YahooFinanceNews.py')
yahooCronJob.setall('30 23 * * 1-5')

# Quandl cronjob, Time: 23:30 - Monday to Friday
quandlCronJob 	= cron.new(command='/usr/bin/python3 /home/advnum/EODQuandl.py')
quandlCronJob.setall('30 23 * * 1-5')

# Names of jobs
jobs 			= [ "Yahoo", "Quandl" ]
# Daytime execution of jobs in "decimals"
times 			= [ "23.5", "23.5" ]

# Writing times to database
cursorObject.execute("INSERT IGNORE INTO Cronjobs (Job, Time) VALUES(%s, %s)",(jobs, times))
connectionObject.commit()



#root = tk()
#root.style = Style()
#root.style.theme.use("clam")
