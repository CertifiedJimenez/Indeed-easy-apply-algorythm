from ast import Break
from accesories import slow_type, element_exists, CustomFieldSelect, clear_field
from selenium.webdriver.common.keys import Keys
from datetime import datetime
import time
import yaml
import json
from pathlib import Path
from csv import writer


# SUCCESS_URL = 'https://secure.indeed.com/settings/account/'
APPLIED_URL = 'https://m5.apply.indeed.com/beta/indeedapply/form/review'

class Indeed_Bot():


    def __init__(self, driver: None):
        self.driver = driver
        self.Job_Search = []
        self.Job_Location = []
        self.FailedPages = 0
        self.skills = []
        self.exclude = []
        self.salary = str
        self.occupdation = str
        self.title = str
        self.company = str
        self.applied_time = str
        self.job_url = str
        pass

    def update(self):
        """
            Updates the config file on launch.
        """
        with open('config.yml', 'r') as file:
            UpdatedInfo = yaml.safe_load(file)

            # Job preferences 
            titles = UpdatedInfo['Perefence']['Search'].split(',')
            for item in titles:
                self.Job_Search.append(item)
            locations = UpdatedInfo['Perefence']['Location'].split(',')
            for item in locations:
                self.Job_Location.append(item)

            skills = UpdatedInfo['Perefence']['Skills'].split(',')
            for item in skills:
                self.skills.append(item)

            exclude = UpdatedInfo['Perefence']['Exclude'].split(',')
            for item in exclude:
                self.exclude.append(item)

    
    def search(self, **kwargs):
        """
            Searches a new Job or location. 
        """

        if 'Index_Title' in kwargs:
            Index_Title = kwargs['Index_Title']
            Index_Location = kwargs['Index_Location']
        else:
            Index_Title = 0
            Index_Location = 0

        self.driver.get('https://www.indeed.co.uk')
        search = self.driver.find_element_by_xpath('//*[@id="text-input-what"]')
        slow_type(search,self.Job_Search[Index_Title])

        location = self.driver.find_element_by_xpath('//*[@id="text-input-where"]') 
        clear_field(location,20)

        slow_type(location,self.Job_Location[Index_Location])
        self.driver.find_element_by_xpath('//*[@id="jobsearch"]/button').click()



    def send_application(self):
        """
            Form handling proccess of submitting an application.
        """

        handels = self.driver.window_handles
        self.driver.switch_to.window(handels[1])
        # Type 01
        try:
            time.sleep(2)
            CustomFieldSelect(self.driver,'//*[@id="ia-container"]/div/div/div/main/div[2]/div[2]/div/div/div[2]/div/button')
        except:
            print('')
        # Type 02
        try:
            time.sleep(1)

            for x in range(6):
                time.sleep(1)
                try:
                    self.driver.find_element_by_xpath('//*[@id="ia-container"]/div/div[1]/div/main/div[2]/div[2]/div/div/div[2]/div/button').click()
                except:
                    time.sleep(1)
                    CustomFieldSelect(self.driver,'//*[@id="ia-container"]/div/div/div/main/div[2]/div[2]/div/div/div[2]/div/button')
                    if self.driver.current_url == APPLIED_URL:
                        self.store_job() # Store the job
 

            # CustomFieldSelect(self.driver,'//*[@id="ia-container"]/div/div[1]/div/main/div[2]/div[2]/div/div/div[2]/div/button')
            # job_title =  self.driver.find_element_by_xpath('//*[@name="jobTitle"]') 
            # slow_type(job_title,self.Search)
            # company_name =  self.driver.find_element_by_xpath('//*[@name="companyName"]') 
            # slow_type(company_name,'rolecatcher.com')
            # CustomFieldSelect(self.driver,'//*[@id="ia-container"]/div/div[1]/div/main/div[2]/div[2]/div/div/div[2]/div/button')
            # CustomFieldSelect(self.driver,'//*[@id="ia-container"]/div/div/div/main/div[2]/div[2]/div/div/div[2]/div/button')
        except Exception as e: print(e)

        self.driver.close()
        self.driver.switch_to.window(handels[0])
        return True



    def allowed_apply(self):
        """
            Checks for any white listed and black listed words
        """
        description = self.driver.find_element_by_xpath('//*[@id="jobDescriptionText"]').get_attribute('innerHTML')
        # checks if match
        if any(word in description for word in self.skills):
            # exclude match
            if any(word in description for word in self.exclude):
                print('exlcuded')
                return False
            else:
                print('match')
                self.FailedPages = 0
                return True

        print('ignored')
        self.FailedPages += 1
        return False


    def store_job(self):
        """
            Saves job to csv for user report.
        """
        list_data = [self.salary,self.occupdation,self.title,self.company,self.applied_time,self.job_url]
        print(list_data)
        with open('savedJobs.csv', 'a', newline='') as f_object:  
            writer_object = writer(f_object)
            writer_object.writerow(list_data)


    def run_searches(self):
        """
            Iterates through the config search requirements files.
        """
        # City 
        for city_index, city in enumerate(self.Job_Location):
            # Title
            for title_index, title in enumerate(self.Job_Search):
                i = 0 # For loop pagination 
                while True:
                    if self.FailedPages < 30: # if failed to get one job on the page then skip to the next search
                        self.load_listings()
                        i += 10
                        current_url = self.driver.current_url
                        locationURL = self.Job_Location[city_index].replace(' ','%20')
                        current_url = current_url.replace(locationURL, locationURL+f"&start={i}")
                        self.driver.get(current_url)
                    else:
                        break
                self.search(Index_Title= title_index,Index_Location=city_index)
            self.search(Index_Title= title_index,Index_Location=city_index)
                

    # Selects all the cards and views the iframes 
    def load_listings(self):
        """
            Loads the card containers and clicks apply now.
        """
        cardListings = self.driver.find_elements_by_class_name('slider_container')
        print(len(cardListings))
        for item in cardListings:
            try:
                item.click()
                self.driver.switch_to.frame(self.driver.find_element_by_xpath('//*[@id="vjs-container-iframe"]'))
                # check here function required 

                if self.allowed_apply():
                    self.applied_time = datetime.now()
                    self.job_url = self.driver.current_url
                    self.salary = self.driver.find_element_by_xpath('//*[@id="salaryInfoAndJobType"]/span[1]').text
                    self.occupdation = self.driver.find_element_by_xpath('//*[@id="salaryInfoAndJobType"]/span[2]').text
                    self.title = self.driver.find_element_by_xpath('//*[@id="viewJobSSRRoot"]/div[2]/div[1]/div/div/div/div[1]/div/div[1]/div[1]/div[1]/div[1]/h1').text
                    self.company = self.driver.find_element_by_xpath('//*[@id="viewJobSSRRoot"]/div[2]/div[1]/div/div/div/div[1]/div/div[1]/div[1]/div[1]/div[2]/div/div/div/div[1]/div[2]/div/a').text
                    self.driver.find_element_by_id('indeedApplyButton').click()

                # new window handle apply now 
                while True:
                    if self.send_application(): break
                self.driver.switch_to.parent_frame()
            except:
                self.driver.switch_to.parent_frame()



    def authenticate(self):
        """
           Stores cookies after logged into the account.
        """
        path = Path('cookies.json')
        if path.is_file():
            # Read cookies
            self.driver.get('https://secure.indeed.com/')
            if self.Load_Account() is not True:
                # Fetch cookeis in case current expires
                self.driver.get('https://secure.indeed.com/')
                while True:
                    if self.successful_login(): break
                return self.Save_Account()
            return True
        else:
            # Fetch cookeis
            self.driver.get('https://secure.indeed.com/')
            while True:
                if self.successful_login(): break
            return self.Save_Account()
           


    def successful_login(self):
            return self.driver.current_url == 'https://secure.indeed.com/settings/account'


    def Save_Account(self):
        # saves cookies
        cookies = self.driver.get_cookies()
        with open('cookies.json', 'w', encoding='utf-8') as f:
            json.dump(cookies, f, ensure_ascii=False, indent=4)
        return True

    def Load_Account(self):
        # adds cookies
        with open('cookies.json', 'r', encoding='utf-8') as f:
            for i in json.load(f):
                self.driver.add_cookie(i)
            self.driver.refresh()
        return self.successful_login()
