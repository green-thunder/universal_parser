import json
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from tqdm import tqdm

driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))

class GatherLinks:
    def __init__(self, filename):
        self.filename = filename
        self.links_list = []  
        self.row_counter = 0

    def collect(self, websites):
        for website in websites:
            url = website['Url']
            css_selector = website['Cssseloctor']
            page_numbers = website['Page_number']
            main_url = website['mainUrl']

            for page_num in tqdm(range(1, page_numbers + 1)):
                url_ = url + str(page_num)
                driver.get(url_)
                time.sleep(3)

                soup = BeautifulSoup(driver.page_source, "lxml")
                dom = soup.select(css_selector)

                for item in dom:
                    link = item.get('href')
                    if main_url not in str(item):
                        full_url = str(main_url) + str(link)
                    else:
                        full_url = link

                    if full_url not in self.links_list:
                        self.links_list.append(full_url)
                        self.row_counter += 1

                    if self.row_counter >= 10:
                        self.save()
                        self.row_counter = 0  

    def save(self):
        with open(self.filename, 'w', encoding='utf-8') as f:
            json.dump(self.links_list, f, ensure_ascii=False, indent=4)
