import re
from urllib.parse import urlparse, urljoin
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import concurrent.futures
import random
import json
from random import choice
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from time import sleep



# Converts sets into a serializable form
class SetEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, set):
            return list(obj)
        return json.JSONEncoder.default(self, obj)


def get_links(url, visited_links=set()):
    sublinks = set()
    options = Options()
    options.headless = True
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(options=options, executable_path="C:\\Users\\user3\\Downloads\\chromedriver.exe")
    driver.get(url)
    sleep(2)
    page_links = [a.get_attribute('href') for a in driver.find_elements_by_xpath('//a[@href]')]
    driver.quit()
    for link in page_links:
        if link:
            parsed_link = urlparse(link)
            if parsed_link.netloc == urlparse(url).netloc and re.search('^/', parsed_link.path) and link not in visited_links:
                visited_links.add(link)
                sublinks.update(get_links(link, visited_links=visited_links))
    return visited_links


def get_emails_names_phones(url, proxies):
    results = {'emails': set(), 'phone_numbers': set(), 'names': set(), 'urls': set()}
    page_links = get_links(url)
    email_pattern = re.compile(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+')
    name_pattern = re.compile(r'[A-Z][a-z]* [A-Z][a-z]*')
    phone_pattern = re.compile(r'\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b')
    for link in page_links:
        link = urljoin(url, link)
        print("Crawling {}".format(link))
        if link.startswith(url):
            proxy_switch = True
            while proxy_switch:
                try:
                    proxy = choice(proxies)
                    proxy_dict = {
                        'http': f'http://{proxy}',
                        'https': f'https://{proxy}'
                    }
                    options = Options()
                    options.headless = True
                    options.add_argument('--disable-gpu')
                    options.add_argument('--no-sandbox')
                    options.add_argument('--disable-dev-shm-usage')
                    # options.add_argument(f'--proxy-server={proxy_dict}')
                    driver = webdriver.Chrome(options=options, executable_path="C:\\Users\\user3\\Downloads\\chromedriver.exe")
                    driver.get(link)
                    sleep(2)
                    html = driver.page_source
                    driver.quit()
                    if '\"msg\":\"This site can’t be reached\"' in html:
                        raise Exception("Proxy connection invalid")
                    emails = email_pattern.findall(html)
                    names = name_pattern.findall(html)
                    phones = phone_pattern.findall(html)
                    results["emails"].update(emails)
                    results["phone_numbers"].update(phones)
                    results["names"].update(names)
                    results["urls"].add(link)
                    proxy_switch = False
                except Exception as e:
                    print(e)
    return results


def start_scraper_threads(url, num_threads, proxies):
    with open(proxies, 'r') as file:
        proxy_list = [line.strip() for line in file]

    results = []
    results = get_emails_names_phones(url, proxy_list)

    return results

with open("sites.txt", "r") as sites_file:
    sites = sites_file.read().splitlines()

for site in sites:
    final_results = start_scraper_threads(site, 1, "socks5_proxies.txt")
    print(final_results)
    with open("{}.json".format(site.split("/")[2]), "w+") as  output:
        output.write(json.dumps(final_results, cls=SetEncoder))
    print("Wrote to file.")


print("Found {} emails".format(len(final_results["emails"])))
print("Found {} names".format(len(final_results["names"])))
print("Found {} phone numbers".format(len(final_results["phone_numbers"])))