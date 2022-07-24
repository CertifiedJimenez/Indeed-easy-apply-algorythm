from ast import Dict
from operator import contains
from selenium import webdriver
from accesories import slow_type, element_exists
from IndeedFunctions import Indeed_Bot
from datetime import datetime

import time


PATH = "msedgedriver.exe"
driver = webdriver.Edge(PATH)


Scrape = Indeed_Bot(driver)
Scrape.update()
if Scrape.authenticate():
    Scrape.search()
    Scrape.run_searches()
    input(' Searches complete ')

