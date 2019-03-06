# AdvNum19_DataServer
First Project

-------------



# Dataserver Project Description

**Elisa FLeissner** &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp;elisa.fleissner@student.unisg.ch <br>
**Lars Stauffenegger** &nbsp; &nbsp; &nbsp;lars.stauffenegger@student.unisg.ch  <br>
**Peter la Cour** &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; peter.lacour@student.unisg.ch

## Overview


* <div id="A1"> <a href="#A2">Setting up the Server </a></div>
* <div id="B1"> <a href="#B2">Installing Firefox on Linux </a></div>
* <div id="C1"> <a href="#C2">The Newspaper Scrape </a></div>
* <div id="D1"> <a href="#D2">Loading the script and Setting up the Cron Job </a></div>
* (Setting up GitHub?)

## <div id="A1"> <a href="#A2">Setting up the Server  </a> </div>


* Initial Setup
* Setting up users 
* Granting Permissions
* Installing Python
* Installing MySql
* Installing Firefox
* etc.





## <div id="B2"> <a href="#B1">Installing Firefox on Linux</a> </div>

To install Firefox on Linux we first add its repository with the command:

```
sudo add-apt-repository ppa:mozillateam/firefox-next
```

Before continuing we update the packages on our server to ensure that the new firefox is compatible:

```
sudo apt-get update
```

Finally, we run the following command to install Firefox:

```
sudo apt-get install firefox
```

However, to use the Firefox webdriver for the Python script we need to add its webdriver `geckodriver`. The webdriver can be downloaded here: https://github.com/mozilla/geckodriver/releases. 
To add geckodriver to the server use  

```
scp /Users/PeterlaCour/Documents/MIQEF/ANMandDA/AdvNum19_DataServer/geckodriver plc@51.75.72.97:/home/advnum
```

to secure copy the file from a local machine to the desired directory on the server.


## <div id="C2"> <a href="#C1">The Newspaper Scrape</a> </div>

* ( What packages are used )
* ( How does the scrape work )
* 
* 
* Description of scraped data




## <div id="D2"> <a href="#D1">Loading the script and Setting up the Cron Job</a> </div>


* importing the script from local machine
* 
* Script writes to news.db on server.. etc.
* 
* Description of Cron Job Setup ( how it was set up when does it execute )
