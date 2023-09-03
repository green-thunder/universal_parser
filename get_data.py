import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
import os
import concurrent.futures

class GatherData:

    def __init__(self, urls):
        self.urls = urls
        self.data_text = []
        self.data_imgs = []
        self.row_counter = 0  
        self.file_number = 1  
        self.max_rows_per_file = 500  

    def parse_text_url(self, url):
        text_list = []
        try:
            response = requests.get(url, timeout=10)  
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            for p_tag in soup.find_all('p'):
                text = p_tag.get_text(strip=True, separator=' ')
                text_list.append(text)
                self.row_counter += 1  
        except Exception as e:
            print(f"Error scraping {url}: {str(e)}")

        return '\n'.join(text_list)

    def parse_images_url(self, url):
        img_sources = []
        try:
            response = requests.get(url, timeout=10)  # Add a timeout for the request
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            images = soup.find_all('img')
            img_sources = [item.get('src') for item in images if item.get('src') and item.get('src').startswith("https")]
        except Exception as e:
            print(f"Error scraping images from {url}: {str(e)}")

        return img_sources

    def save_text(self):
        with open(f'datasets/textdataset_{self.file_number}.txt', 'a', encoding='utf-8') as f:
            f.write('\n'.join(self.data_text))

    def save_images(self):
        with open(f'datasets/imagesdataset_{self.file_number}.txt', 'a', encoding='utf-8') as f:
            f.write('\n'.join(self.data_imgs))

    def parse_and_save_text(self, url):
        text = self.parse_text_url(url)
        self.data_text.append(text)

        if self.row_counter >= self.max_rows_per_file:
            self.save_text()
            self.data_text = []
            self.row_counter = 0
            self.file_number += 1  # Increment the file number

    def parse_and_save_images(self, url):
        img_sources = self.parse_images_url(url)
        self.data_imgs.extend(img_sources)

        if self.row_counter >= self.max_rows_per_file:
            self.save_images()
            self.data_imgs = []
            self.row_counter = 0
            self.file_number += 1  # Increment the file number

    def perform_operations(self, parse_text=False, parse_images=False, save_text=False, save_images=False):
        with concurrent.futures.ThreadPoolExecutor() as executor:
            if parse_text:
                list(tqdm(executor.map(self.parse_and_save_text, self.urls), total=len(self.urls)))

            if parse_images:
                list(tqdm(executor.map(self.parse_and_save_images, self.urls), total=len(self.urls)))

        if save_text:
            self.save_text()

        if save_images:
            self.save_images()
