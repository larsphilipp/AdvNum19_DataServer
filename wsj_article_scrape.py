
## Title:        WSJ Article Scrape
## Author:       Elisa FLeissner, Lars Stauffenegger, Peter la Cour
## Email:        elisa.fleissner@student.unisg.ch,
##               lars.stauffenegger@student.unisg.ch,
##               peter.lacour@student.unisg.ch
## Place, Time:  St. Gallen, 05.03.19
## Description:  Script scrapes all articles from the Wall Street Journal including
##               headlines, article category, authors, and the visible article introduction
## Improvements: -
## Last changes: -

#-----------------------------------------------------------------------------#
# Loading Packages
#-----------------------------------------------------------------------------#
import pandas as pd
import numpy as np
from sqlalchemy import create_engine
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import sqlalchemy as db
from sqlalchemy import update
from selenium.webdriver.firefox.options import Options


#-----------------------------------------------------------------------------#
# Functions
#-----------------------------------------------------------------------------#


#-----------------------------------------------------------------------------#
# Body
#-----------------------------------------------------------------------------#

# loading database
engine = db.create_engine('sqlite:////home/advnum/wsj.db') # sqlite:////Users/PeterlaCour/Documents/Research/News/news.db

# loading webdriver
options = Options()
options.headless = True
driver = webdriver.Firefox(executable_path=r'/home/advnum/webdriver/geckodriver', options = options)


# create empty dataframe with given columns
columns                 = [ "Category", "Link", "Headline", "Sub-Headline", "Authors", "Timestamp", "Content" ]
wsj_articles_df         = pd.DataFrame(columns = columns)
url                     = "https://www.wsj.com/europe"
driver.get(url)
# get all links of articles on the Wall Street Journal website with the form www.wsj.com/articles/...
links                   = [ link.get_attribute("href") for link in driver.find_elements_by_class_name('wsj-headline-link') if "www.wsj.com/articles/" in link.get_attribute("href") ]


# loop to scrape the article information
for l in range(len(links)):
    driver.get(links[ l ])
    # get the web-element that includes category, header and subheader
    try:
        temp            = driver.find_element_by_class_name('wsj-article-headline-wrap')
        try:
            category    = temp.find_element_by_class_name("category").text
        except:
            pass
        headline        = temp.find_element_by_class_name("wsj-article-headline").text
        subheader       = temp.find_element_by_class_name("sub-head").text
    except:
        pass
    try:
        # get the web-element that includes authors, timestamp of the article and the visible content
        temp            = driver.find_element_by_class_name('snippet')
        try:
            # get the list of authors of a given article and joins them with a "," for easier analysis
            authors     = ",".join([ name.text for name in temp.find_element_by_class_name("byline").find_elements_by_class_name("name") ])
        except:
            pass
        timestamp       = temp.find_element_by_class_name("article__timestamp").text
        # get the visible article content and replaces new lines with a space
        content         = temp.find_element_by_class_name("wsj-snippet-body").text.replace("\n", " ")
    except:
        pass
    # write the scraped data to a dataframe
    wsj_articles_df     = wsj_articles_df.append({ "Category": category, "Link": links[ l ], "Number": l, "Content": content, "Headline": headline, "Sub-Headline": subheader, "Authors": authors, "Timestamp": timestamp }, ignore_index = True)

# quit webdriver
driver.quit()
wsj_articles_df.to_sql(name = "wsj_articles", con = engine, if_exists='append')
connection.close()
