import requests
from bs4 import BeautifulSoup
from unidecode import unidecode
import re
import pandas as pd


#
class BaladCrawler:
    def __init__(self, start_url):
        # initialize the crawler
        self.start_url = start_url

    @staticmethod
    def has_no_class(tag):
        # for crawl category of each restaurant
        return tag.name == 'div' and not tag.has_attr('class')

    def crawl(self):
        # main method for crawl
        page_number = 1
        results = []

        while True:
            url = f"{self.start_url}?page={page_number}"
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            # list all item in page = [page_number]
            items = soup.find_all('div', class_='BundleItem_item__texts__2l15O')

            if not items:
                break

            for item in items:
                # extract the features of each restaurant
                name = item.find('h2', class_='BundleItem_item__name__1DYyY').text.strip()
                rate = item.find('span', class_='RatingDetail_ratingValue__3uM_E')
                review_text = item.find('span', class_='RatingDetail_ratingCount__Hl21f')
                location = item.find('p', class_='BundleItem_item__subtitle__2a2IA').text.strip()
                categories = item.find_all(self.has_no_class)
                category = ' '.join(category.text.strip() for category in categories if category.text.strip())

                if not rate:
                    rate = 'null'
                else:
                    rate = unidecode(rate.text.strip())

                if not review_text:
                    review = 'null'
                else:
                    review = re.findall(r'\d+', review_text.text)[0] if re.findall(r'\d+', review_text.text) else 'null'

                data = {
                    'name': name,
                    'rate': rate,
                    'review': review,
                    'category': category,
                    'location': location
                }

                results.append(data)

            page_number += 1

        return results


# Usage
start_url = 'https://balad.ir/city-rafsanjan/cat-restaurant'
crawler = BaladCrawler(start_url)
data = crawler.crawl()


df = pd.DataFrame(data)
df.to_csv('BaladDataset.csv', index=True)