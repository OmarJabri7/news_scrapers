from utils import *
import json
import pandas as pd
import logging
import os

import zipfile

def unzip_folder(zip_path, extract_path):
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_path)

# Configure logger
logging.basicConfig(level=logging.INFO,
                    format='[%(asctime)s] [%(levelname)s] %(message)s')

# Create a logger instance
logger = logging.getLogger(__name__)


if __name__ == "__main__":

    if not os.path.exists("firefox"):
        unzip_folder("firefox.zip", ".")

    """Get user query and parse/clean it"""
    start_time = dt.datetime.today()
    logger.info(f"Started execution at {start_time}")
    user_input = input("User query:\n")
    user_input = parse_user_input(user_input)

    """Get Date range for google query"""
    date_range = get_dates(days=90)

    """Determine what the OS running this file is, to use correct executable"""
    os_driver = determine_os_driver()

    """Generate Cookies"""
    get_cookies("https://www.google.com", os_driver)
    """Get articles from webdriver"""
    """If you want to see what bot is doing on the browser, turn headless to False"""
    articles = list(get_articles(user_input, date_range, os_driver, headless=True))

    """Parse and extract article data"""
    data = [parse_article(article)
            for article in articles]
    """Remove None values"""
    data = [element for element in data if element]

    if not os.path.exists('jsons'):
        os.makedirs('jsons')
    if not os.path.exists('csvs'):
        os.makedirs('csvs')
    """Dump dict data into JSON file specific to User input"""
    try:
        with open(f"jsons/{user_input}_{dt.datetime.today().strftime('%d-%b-%Y')}.json", 'w') as f:
            """Convert the dictionary to JSON and write it to the file"""
            json.dump(data, f)
    except Exception as e:
        logger.error(e, exc_info=True)

    """Dump dict data into CSV file specific to User input"""
    try:
        df = pd.DataFrame(data)
        df.to_csv(
            f"csvs/{user_input}_{dt.datetime.today().strftime('%d-%b-%Y')}.csv", index=False)
    except Exception as e:
        logger.error(e, exc_info=True)
    end_time = dt.datetime.today()
    logger.info(f"Finished execution at {end_time}")
    logger.info(f"Execution took {end_time - start_time}")
