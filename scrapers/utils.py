import requests
import bs4
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options
import pickle
import logging
import datetime as dt
from typer import Typer
import sys
import time
from urllib3.exceptions import NewConnectionError

"""Configure logger"""
logging.basicConfig(level=logging.INFO,
                    format='[%(asctime)s] [%(levelname)s] %(message)s')

"""Create a logger instance"""
logger = logging.getLogger(__name__)

def determine_os_driver():
    if 'win' in sys.platform:
        return 'win'
    return 'linux'


def get_dates(days=90):
    """Extract data from last 90 days by default or n days"""
    end_date = dt.date.today()
    start_date = dt.date.today() - dt.timedelta(days=days)
    date_range = f"after:{start_date.strftime('%Y-%m-%d')} before:{end_date.strftime('%Y-%m-%d')}"
    logging.info(f"Generating date range of format {date_range}")
    return date_range


def get_cookies(url, os_driver):
    """Get firefox cookies and save for later use if not already stored"""
    firefox_options = Options()
    firefox_options.headless = True
    firefox_options.binary_location = "firefox/firefox.exe"
    logger.info("Extracting cookies...")
    driver = webdriver.Firefox(options=firefox_options, executable_path=f'./drivers/{os_driver}')
    driver.get(url)
    with open("cookies.pkl", "wb") as f:
        pickle.dump(driver.get_cookies(), f)
    driver.quit()


def parse_user_input(usr_input):
    """Remove all special and unknown charachters from user input"""
    clean_text = re.sub(r'[^a-zA-Z0-9\s]', ' ', usr_input)
    return clean_text.strip()


def remove_js(soup):
    """Extract and remove all scripts in html"""
    for script in soup.find_all('script'):
        script.extract()
    """Create pattern to remove"""
    pattern = re.compile(r'<[^>]*? on\w+="[^"]*"[^>]*?>')

    """Execute removal"""
    soup = bs4.BeautifulSoup(
        re.sub(pattern, '', str(soup)), "lxml")
    return soup


def get_articles(user_input, user_date, os_driver, page=1, driver=None, headless=True):
    """Setup webdriver, with headless = true (so no popups)"""
    if not driver:
        firefox_options = Options()
        firefox_options.headless = headless
        firefox_options.binary_location = "firefox/firefox.exe"
        driver = webdriver.Firefox(options=firefox_options, executable_path=f'./drivers/{os_driver}')
        driver.get("http://www.google.com")

        """Load existing cookies for increased efficiency"""
        with open("cookies.pkl", "rb") as f:
            cookies = pickle.load(f)
        for cookie in cookies:
            driver.add_cookie(cookie)
        logger.info("Accepting google user agreement...")
        """Accept the google user agreement"""
        accept_all_button = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.ID, "L2AGLb"))
        )
        accept_all_button.click()


        """Setup query and find element search input and send query"""
        query = f"site:unite.ai {user_date} {user_input}"
        logger.info(f"Setup query: {query} and returning results...")
        element = driver.find_element(By.NAME, "q")
        """Mimic human behavior by typing with typos and correcting them in real time."""
        ty = Typer(accuracy=0.9, correction_chance=0.50,
                typing_delay=(0.04, 0.08), distance=2)
        ty.send(element, query)
        element.submit()

    """Wait until search results load"""
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "search")))

    """Get the search result URLs"""

    search_results = driver.find_elements(By.TAG_NAME, "a")
    urls = [result.get_attribute(
        "href") for result in search_results if result.get_attribute("href")]

    """Get articles based on main site and convert them into Soup objects"""
    articles = [(url, remove_js(bs4.BeautifulSoup(requests.get(url).content, "lxml")))
                for url in urls if "https://www.unite.ai/" in url]
    logger.info(f"Extracted articles from results, page: {page}")

    """Add articles to generator object (more efficient than lists)"""

    yield from articles

    """Check if there are any other pages"""
    next_button = driver.find_elements(
        By.XPATH, f'//a[@aria-label="Page {page + 1}"]') if driver.find_elements(
        By.XPATH, f'//a[@aria-label="Page {page + 1}"]') else None

    """Recursively navigate to the next page if it exists"""
    if next_button:
        next_button[0].click()
        """Repeat function for next page and yield result to generator"""
        yield from get_articles(user_input, user_date, os_driver, page=page+1, driver=driver)
    else:
        """Close web driver connection"""
        driver.quit()


def parse_article(article):
    article_data = dict()
    """Find each class within article, try for one index then another if fails"""
    try:
        try:
            article_data["Category"] = article[1].find(
                "meta", property="article:section")['content']
        except:
            try:
                article_data["Category"] = article[1].find(
                    "meta", property="og:section")['content']
            except:
                article_data["Category"] = None
        try:
            article_data["Title"] = article[1].find(
                "meta", property="og:title")['content'].replace('”', '').replace("“", '').replace('"', '')
        except:
            article_data["Title"] = article[1].find(
                "meta", property="article:title")['content'].replace('”', '').replace('"', '')
        try:
            article_data["URL"] = article[1].find(
                "meta", property="og:url")['content']
        except:
            article_data["URL"] = article[1].find(
                "meta", property="article:url")['content']
        try:
            article_data["Date"] = article[1].find(
                "meta", property="article:updated_time")['content']
        except:
            article_data["Date"] = article[1].find(
                "meta", property="og:updated_time")['content']
        try:
            article_data["Description"] = article[1].find(
                "meta", property="og:description")['content']
        except:
            article_data["Description"] = article[1].find(
                "meta", property="article:description")['content']
        """Clean Body text from Watch Youtube and Links"""
        body_text =  article[1].find(
            'div', id='mvp-content-main').get_text(separator="\n").replace("Watch this video on YouTube", "")
        body_text = re.sub(r'https?://\S+', '', body_text)
        article_data["Body"] = body_text
        logger.info(f'Storing article {article_data["Title"]}')
    except:
        """Failed because the article is not an article (author info, tags, research papers...)"""
        logger.error(
            f"Failed saving article: {article[0]}")
        return None
    return article_data
