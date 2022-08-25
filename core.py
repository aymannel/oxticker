from datetime import datetime
from time import sleep
import pandas as pd
import logging
import random
import json
import sys

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.common.exceptions import TimeoutException

#logging options
logging.basicConfig(level=logging.INFO, format='(%(levelname)-s) %(asctime)s %(message)s', datefmt='%d-%m %H:%M:%S')

class FacebookScraper():
    def __init__(self):
        option = Options() #browser options
        option.add_argument('--incognito')
        option.add_argument("--disable-infobars")
        option.add_argument('--disable-extensions')
        option.add_argument('--ignore-certificate-errors')

        self.driver = webdriver.Firefox(service=Service("./geckodriver"), options=option)
        self.driver.maximize_window()
        logging.info('FirefoxWebDriver object initialised')
        
        try:
            with open("credentials.json") as file:
                credentials = json.load(file)

            self.email = credentials['name']
            self.password = credentials['password']
            logging.info("'credentials.json' loaded")
            
        except FileNotFoundError:
            logging.error("'credentials.json' file not found")

        logging.info('FacebookScraper object initialised')


    def login(self):
        logging.info('Get "https://facebook.com"')
        self.driver.get("https://facebook.com")
        self.waits(2, 4)

        self.wait = WebDriverWait(self.driver, 5) #change wait time back to 30
        logging.info("WebDriverWait object initialised")
        
        try:
            xpath_accept_cookies = "//button[contains(string(), 'Only allow essential cookies')]"
            self.accept_cookies = self.wait.until(EC.element_to_be_clickable((By.XPATH, xpath_accept_cookies))).click() #accept cookies
            logging.info('Sent click: accept essential cookies')
            self.waits(2, 4)
        except TimeoutException:
            pass


        logging.info(f'Send keys = "{self.email}"')
        self.email_field = self.wait.until(EC.visibility_of_element_located((By.NAME, 'email'))) #send keys email
        self.email_field.send_keys(self.email)
        self.waits(2, 4)

        logging.info(f'Send keys = "' + "*"*len(self.password) + '"')
        self.pass_field = self.wait.until(EC.visibility_of_element_located((By.NAME, 'pass'))) #send keys password
        self.pass_field.send_keys(self.password)
        self.waits(2, 4)

        logging.info('Send click: Keys.RETURN')
        self.pass_field.send_keys(Keys.RETURN)

        while "LoggedIn" not in self.driver.page_source:
            sleep(1)
        logging.info("Successful log-in")
        self.waits(2, 4)


    def get_page(self, page_url):
        logging.info(f'Get = "{page_url}"')
        self.driver.get(page_url)
        self.waits(8, 12)


    def get_html(self):
        logging.info('BeautifulSoup object initialised') #DONT initialise bs4 every time u get html!?!?!
        self.soup = BeautifulSoup(self.driver.page_source, "lxml")
        identifier = datetime.now().strftime('%H:%M:%S')

        with open(f'data/source_{identifier}.txt', 'w') as file:
            logging.info('Commit page source to file')
            file.write(self.soup.prettify())
            file.close()
        
        return self.soup

    def waits(self, lower, upper):
        sleep(random.uniform(lower, upper))


    def teardown(self):
        self.driver.close()
        logging.info('WebDriver connection closed')


class Parser():
    def __init__(self, soup='./data/source.txt'):
        if type(soup) == str:
            with open(soup) as file:
                self.soup = BeautifulSoup(file, "lxml")
        else:
            self.soup = soup
            
        self.soup.prettify()
        self.posts_all = self.soup.select('div[class="du4w35lb k4urcfbm l9j0dhe7 sjgh65i0"]')

        self.post_content = [None]*len(self.posts_all)
        self.post_title = [None]*len(self.posts_all)
        self.post_price = [None]*len(self.posts_all)
        self.post_name = [None]*len(self.posts_all)
        self.post_location = [None]*len(self.posts_all)
        self.post_comment_number = [None]*len(self.posts_all)


    def get_post_titles(self):
        for idx, post in enumerate(self.posts_all):
            tags = post.select('span[class="a8c37x1j ni8dbmo4 stjgntxs l9j0dhe7"]')
            self.post_title[idx] = tags[0].get_text().strip() #retrieve post title
            #error handler
    

    def get_post_content(self):
        for idx, post in enumerate(self.posts_all):
            content = post.select('div[class="kvgmc6g5 cxmmr5t8 oygrvhab hcukyx3x c1et5uql ii04i59q"]')
            if len(content) > 0:
                self.post_content[idx] = ' '.join(content[0].get_text().split())
            else:
                self.post_content[idx] = 'no content'
            #error handler
            
    
    def get_post_names(self):
        for idx, post in enumerate(self.posts_all):
            tags = post.select('span[class="a8c37x1j ni8dbmo4 stjgntxs l9j0dhe7"]')
            self.post_name[idx] = tags[1].get_text().strip() #retrieve post name
            #error handler

    
    def get_post_prices_locations(self):
        for idx, post in enumerate(self.posts_all):
            parent_objects = post.select('span[class="sqxagodl"]')[0].get_text().strip()
            tags = [line.strip() for line in parent_objects.split('\n') if line.strip() != '']
    
            if len(tags) == 3:
                self.post_price[idx] = tags[0]
                self.post_location[idx] = tags[2]
            elif 'Contact seller' in tags:
                self.post_price[idx] = 'contact seller'
            elif len(tags) == 1:
                self.post_price[idx] = tags[0]


    def get_comment_number(self):
        for idx, post in enumerate(self.posts_all):
            tags = post.find_all('h3', class_="gmql0nx0 l94mrbxd p1ri9a11 lzcic4wl q45zohi1 ema1e40h ay7djpcl ni8dbmo4 stjgntxs pmk7jnqg rfua0xdk")
            text = tags[0].get_text().strip()
            comment_number = [int(s) for s in text.split() if s.isdigit()][0]
            self.post_comment_number[idx] = comment_number


    def compile_data(self):
        self.data = { 'name': self.post_name,
                      'title': self.post_title,
                      'content': self.post_content,
                      'price': self.post_price,
                      'location': self.post_location,
                      'no. comments': self.post_comment_number }

        identifier = datetime.now().strftime('%H:%M:%S')
        self.frame = pd.DataFrame(self.data)
        self.frame.to_csv(f'data/dump_{identifier}.csv', index=False)
    

    def print_data(self):
        print(self.frame, '\n\n')
#        for content in self.frame['content']:
#            print(content, '\n')
