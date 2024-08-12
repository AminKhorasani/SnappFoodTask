from SnappFoodCrawler import RestaurantScraper
from DataProcessing import process_data
from DB import save_data

driver_path = '/usr/local/bin/chromedriver'
url = 'https://snappfood.ir'


def main():
    # Crawl data
    scraper = RestaurantScraper(driver_path, url)
    path = scraper.run()

    # Process the data
    processed_data = process_data(path)

    # Save processed data to the database
    save_data(processed_data)


if __name__ == "__main__":
    main()
