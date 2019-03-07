#!/usr/bin/env python3

## Title:        WSJ and FT Top Stories Scrape
##
## Authors:      Elisa FLeissner, Lars Stauffenegger, Peter la Cour
##
## Email:        elisa.fleissner@student.unisg.ch,
##               lars.stauffenegger@student.unisg.ch,
##               peter.lacour@student.unisg.ch
##
## Place, Time:  St. Gallen, 05.03.19
##
## Description:  Script scrapes all top articles from the Wall Street Journal and
##               the Financial Times, including headline, description (if available),
##               article link and the date it was scraped
## Improvements: -
## Last changes: -

#-----------------------------------------------------------------------------#
# Loading Packages
#-----------------------------------------------------------------------------#
import pandas as pd
import numpy  as np
from sqlalchemy import create_engine
import pymysql
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
import datetime
import sqlalchemy as db
from sqlalchemy import update
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
#-----------------------------------------------------------------------------#
# Functions
#-----------------------------------------------------------------------------#

#-----------------------------------------------------------------------------#
# Body
#-----------------------------------------------------------------------------#



# Loading database
engine = db.create_engine('mysql+pymysql://root:advnum19@localhost/dataserver') # sqlite:////Users/PeterlaCour/Documents/Research/News/news.db
connection = engine.connect()

# Setting up webdriver
firefox_capabilities = DesiredCapabilities.FIREFOX
firefox_capabilities['marionette'] = True
firefox_capabilities['binary'] = '/usr/bin/firefox'
options                 = Options()
options.headless = True
driver                  = webdriver.Firefox(capabilities=firefox_capabilities, executable_path=r'geckodriver', options = options)

# Creating DataFrame to write to database
columns                 = [ "Date Extracted", "Headline", "Description", "Link", "Number"]
news_df                 = pd.DataFrame(columns = columns)
today                   = datetime.datetime.today().strftime('%Y-%m-%d')

# Top WSJ Stories Scrape
url                     = "https://www.wsj.com/europe"
driver.get(url)
content                 = driver.find_element_by_class_name('lead-story').find_elements_by_class_name('wsj-card')
# headline
for n in range(len(content)):
    headline            = content[n].find_element_by_class_name('wsj-headline-link').text
    try:
        description     = content[n].find_element_by_class_name('wsj-summary').text
    except:
        pass
    link                = content[n].find_element_by_class_name('wsj-headline-link').get_attribute('href')
    news_df             = news_df.append({"Date Extracted": today, "Headline": headline, "Link": link, "Number": n+1, "Description": description, "Newspaper": "WSJ" }, ignore_index = True)



# Top FT Stories Scrape
url                     = "https://www.ft.com/"
driver.get(url)
content                 = driver.find_element_by_class_name('top-stories').find_elements_by_class_name('o-teaser__content')
for k in range(len(content)):
    # header
    headline            = content[k].find_element_by_class_name('o-teaser__heading').text
    # description
    try:
        description     = content[k].find_element_by_class_name('o-teaser__standfirst').text
    except:
        pass
    # link
    link                = content[k].find_element_by_tag_name('a').get_attribute('href')
    # topic
    topic               = content[k].find_element_by_class_name('o-teaser__meta').text
    news_df             = news_df.append({"Date Extracted": today, "Headline": headline, "Description": description,"Number": k+1, "Link": link, "Newspaper": "FT" }, ignore_index = True)

# Writing DataFrame to database
news_df.to_sql(name = "Top_Stories", con = engine, if_exists='append')

# Quitting webdriver
driver.quit()

# CLosing database connection
connection.close()

print("Database updated.")
