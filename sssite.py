import os
import re
import time
import logging
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from bs4 import BeautifulSoup
import requests
import urllib
import pickle
import argparse

CACHE_FILENAME = 'visited_urls_cache.pkl'
LOG_FILENAME = 'website_screenshot_log.txt'
logging.basicConfig(filename=LOG_FILENAME, level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

VISITED_URLS = set()

def load_visited_urls():
    global VISITED_URLS
    if os.path.exists(CACHE_FILENAME):
        with open(CACHE_FILENAME, 'rb') as f:
            VISITED_URLS = pickle.load(f)
            logging.info(f"Loaded {len(VISITED_URLS)} URLs from cache")

def save_visited_urls():
    with open(CACHE_FILENAME, 'wb') as f:
        pickle.dump(VISITED_URLS, f)
        logging.info(f"Saved {len(VISITED_URLS)} URLs to cache")

def sanitize_domain(domain):
    # Replace non-alphanumeric characters (except '-') with underscores
    safe_domain = re.sub(r'[^a-zA-Z0-9-]', '_', domain)
    safe_domain = safe_domain.strip('_')
    return safe_domain[:255]  # Reasonable filesystem length limit

def fetch_urls(domain, url):
    try:
        VISITED_URLS.add(url)

        req = urllib.request.Request('https://amplify.com/')
        req.add_header('Referer', 'http://mikegrouchy.com')
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:106.0) Gecko/20100101 Firefox/106.0')
        req.add_header('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8')
        req.add_header('Accept-Language', 'en-US,en;q=0.5')

        response = urllib.request.urlopen(req).read().decode('utf-8')
        soup = BeautifulSoup(response, 'html.parser')
        for link in soup.find_all('a', href=True):
            abs_url = requests.compat.urljoin(url, link['href'])

            if domain in abs_url and abs_url not in VISITED_URLS:
                VISITED_URLS.add(abs_url)
                logging.info(f"Found URL: {abs_url}")
                fetch_urls(domain, abs_url)
    except Exception as e:
        logging.error(f"Failed to fetch URLs from {url}: {e}")

def capture_screenshots(driver, domain, output_dir='screenshots'):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # create a directory in the screenshots folder using domain
    output_dir = os.path.join(output_dir, sanitize_domain(domain
                              if domain else 'images'))

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        logging.info(f"Created directory for domain: {domain}")

    for url in VISITED_URLS:
        try:
            driver.get(url)

            # Get the scroll height of the entire page
            scroll_height = driver.execute_script("return document.body.scrollHeight")
            if scroll_height < 600:
                scroll_height = 600
                
            # Set window size to match the page height
            driver.set_window_size(1920, scroll_height)

            # Save the screenshot
            filename = f"{output_dir}/{url.replace('https://', '').replace('/', '_')}.png"
            driver.save_screenshot(filename)
            logging.info(f"Saved full-page screenshot for {url} as {filename}")

            time.sleep(1)  # Be respectful, avoid overwhelming the server
        except WebDriverException as e:
            logging.error(f"Failed to capture screenshot for {url}: {e}")

def main():
    parser = argparse.ArgumentParser(description='Website Screenshot Tool')
    parser.add_argument('domain', help='The domain to capture screenshots from')
    parser.add_argument('start_url', help='The starting URL to begin crawling')

    args = parser.parse_args()

    load_visited_urls()  # Load cache if it exists

    if args.start_url not in VISITED_URLS:
        fetch_urls(args.domain, args.start_url)

    save_visited_urls()  # Save cache after fetching URLs

    # Set up Selenium WebDriver
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    driver = webdriver.Chrome(options=options)

    try:
        capture_screenshots(driver, args.domain)
    finally:
        driver.quit()

if __name__ == '__main__':
    main()