#!/usr/bin/env python3

## Title:        WSJ and FT Top Stories Scrape
## Author:       Elisa FLeissner, Lars Stauffenegger, Peter la Cour
## Email:        elisa.fleissner@student.unisg.ch,
##               lars.stauffenegger@student.unisg.ch,
##               peter.lacour@student.unisg.ch
## Place, Time:  St. Gallen, 05.03.19
## Description:
##
## Improvements: -
## Last changes: -

#-----------------------------------------------------------------------------#
# Loading Packages
#-----------------------------------------------------------------------------#
import pandas as pd
from sqlalchemy import create_engine
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
import datetime
import sqlalchemy as db
from sqlalchemy import update

# loading database
engine = db.create_engine('sqlite:////home/advnum/news.db') # sqlite:////Users/PeterlaCour/Documents/Research/News/news.db
connection = engine.connect()


# Load Database
today = datetime.datetime.today().strftime('%Y-%m-%d')
options = Options()
options.headless = True
driver = webdriver.Firefox(executable_path=r'/home/advnum/geckodriver.log', options = options)

columns = [ "Date Extracted", "Headline", "Description", "Link", "Number"]
news_df = pd.DataFrame(columns = columns)

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
        description     = "na"
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

news_df.to_sql(name = "Top_Stories", con = engine, if_exists='append')
driver.quit()
connection.close()

print("Success!")
