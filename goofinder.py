import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import concurrent.futures


# read proxies from file
with open('proxies.txt', 'r') as f:
    proxies = f.read().splitlines()

def scrape_website(url):
    # set up session with random proxy
    print("Crawling ${url}")

    proxy = {'http': proxies.pop(0)}
    session = requests.Session()
    session.proxies = proxy

    # get website content
    try:
        res = session.get(url)
    except:
        # switch proxy if connection fails
        proxies.append(proxy['http'])
        proxy = {'http': proxies.pop(0)}
        session.proxies = proxy
        res = session.get(url)

    soup = BeautifulSoup(res.content, 'html.parser')

    # find email addresses, phone numbers and names
    emails = set(re.findall(r'[\w\.-]+@[\w\.-]+', soup.get_text()))
    phone_numbers = set(re.findall(r'\d{10,}', soup.get_text()))
    names = set(re.findall(r'[A-Z][a-z]* [A-Z][a-z]*', soup.get_text()))

    # find links to subdomains and subdirectories
    links = set()
    for link in soup.find_all('a'):
        href = link.get('href')
        if href:
            parsed_href = urlparse(href)
            parsed_url = urlparse(url)
            if parsed_href.netloc == parsed_url.netloc and (parsed_href.path.startswith(parsed_url.path) or parsed_href.path == parsed_url.path+'/'):
                links.add(href)
    # scrape subdomains and subdirectories with asynchronous threading
    results = {'emails': emails, 'phone_numbers': phone_numbers, 'names': names}
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(scrape_website, link) for link in links if link.startswith('http') or link.startswith('/')]
        for future in concurrent.futures.as_completed(futures):
            sub_results = future.result()
            results['emails'].update(sub_results['emails'])
            results['phone_numbers'].update(sub_results['phone_numbers'])
            results['names'].update(sub_results['names'])

    # return results
    return results 

sites = []

emails = set()
names = set()
phone_numbers = set()

for site in sites:
    final_results = scrape_website(site)
    emails.update(final_results['emails'])
    names.update(final_results['names'])
    phone_numbers.update(final_results['phone_numbers'])

