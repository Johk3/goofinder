import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin

# read proxies from file
with open('proxies.txt', 'r') as f:
    proxies = f.read().splitlines()

def scrape_website(url):
    # set up session with random proxy
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

    # scrape subdomains and subdirectories
    for link in links:
        if link.startswith('http'):
            scrape_website(link)
        elif link.startswith('/'):
            scrape_website(parsed_url.scheme+'://'+parsed_url.netloc+link)

    # return results
    return emails, names, phone_numbers 

sites = []

emails = set()
names = set()
phone_numbers = set()

for site in sites:
    print("Crawling ${site}")
    new_emails, new_names, new_phone_numbers = scrape_website(site)
    emails.update(new_emails)
    names.update(new_names)
    phone_numbers.update(new_phone_numbers)

