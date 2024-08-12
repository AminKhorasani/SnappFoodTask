import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from unidecode import unidecode
import time
import pandas as pd

class RestaurantScraper:
    def __init__(self, driver_path, url):
        self.driver_path = driver_path
        self.url = url
        self.driver = self.initialize_driver()
        self.restaurants_data = []

    def initialize_driver(self):
        webdriver_service = Service(self.driver_path)
        driver = webdriver.Chrome(service=webdriver_service)
        return driver

    def navigate(self):
        self.driver.get(self.url)
        self.driver.maximize_window()

    def click_link(self):
        link_element = self.driver.find_element(By.XPATH, '//a[@href="/service/all/city/rafsanjan?page=0"]')
        link_element.click()

    def click_button(self, link, xpath):
        try:
            location_button = WebDriverWait(self.driver, 6).until(
                EC.element_to_be_clickable((By.XPATH, xpath)))
            location_button.click()
        except TimeoutException:
            print(f"Skip button not clickable at {link}, skipping...")

    def wait_for_presence(self):
        WebDriverWait(self.driver, 6).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div[class='sc-citwmv iMkliF']")))

    def scroll_page(self):
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        while True:
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(5)
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

    def get_optional_text(self, locator, default="Not Available"):
        try:
            element = WebDriverWait(self.driver, 3).until(EC.visibility_of_element_located((By.XPATH, locator)))
            return element.text
        except TimeoutException:
            return default

    def collect_data_from_restaurants(self):
        restaurants_links = [my_elem.get_attribute("href") for my_elem in WebDriverWait(self.driver, 20).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div[class='sc-citwmv iMkliF'] > a[href]")))]
        for index, link in enumerate(restaurants_links):
            self.driver.get(link)
            self.click_button(link, location_button_path)
            restaurant_info = self.extract_restaurant_data(link)
            if restaurant_info:
                self.restaurants_data.append(restaurant_info)
                print(f'{index + 1} from {len(restaurants_links)}')

    def extract_restaurant_data(self, link):
        discount = self.get_optional_text(discount_path)
        self.click_button(link, rest_data_button_path)

        restaurant_info = {
            'Name': self.get_optional_text(rest_name_path),
            'Location': self.get_optional_text(location_path),
            'Discount': discount,
            'Rate': unidecode(self.get_optional_text(rate_path)),
            'Review': unidecode(self.get_optional_text(review_path)),
            'Category': self.get_optional_text(category_path),
            'Minimum Purchase': int(re.search(r'\d+', self.get_optional_text(min_purchase_path, '0')).group(0))
        }

        return restaurant_info

    def save_to_csv(self, filename):
        df = pd.DataFrame(self.restaurants_data)
        df.to_csv(filename, index=False)
        print(f"Data collection complete and saved to '{filename}'")

    def run(self):
        self.navigate()
        self.click_link()
        self.wait_for_presence()
        self.scroll_page()
        self.collect_data_from_restaurants()
        self.save_to_csv('Datasets/SnappFoodDataset.csv')
        self.driver.quit()


# Usage
# Clickable
location_button_path = '/html/body/div[2]/div/div/div[1]/button'
rest_data_button_path = '/html/body/div[1]/div/main/div/aside[1]/div/section/div/button'

# Locator
rest_name_path = '/html/body/div[2]/div/div/div/div/div[2]/div/div/p[1]'
location_path = '/html/body/div[2]/div/div/div/div/div[2]/div/div/p[3]'
rate_path = '/html/body/div[2]/div/div/div/section/div[1]/div[1]/p[1]'
review_path = '/html/body/div[2]/div/div/div/section/div[1]/div[1]/p[2]/span[2]'
category_path = '/html/body/div[2]/div/div/div/div/div[2]/div/div/p[2]'
discount_path = '/html/body/div[1]/div/main/div/aside[1]/div/section/header/div[2]/div/span'
min_purchase_path = '/html/body/div[2]/div/div/div/div/div[3]/div[3]/div/div/div/span'


driver_path = '/usr/local/bin/chromedriver'
url = 'https://snappfood.ir'
scraper = RestaurantScraper(driver_path, url)
scraper.run()