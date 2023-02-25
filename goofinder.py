import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin

def get_links(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    links = set()

    for link in soup.find_all('a'):
        href = link.get('href')
        if href and urlparse(href).netloc == urlparse(url).netloc:
            links.add(urljoin(url, href))

    return links

def extract_info(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    emails = set(re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', soup.get_text()))
    names = set(re.findall(r'\b[A-Z][a-z]+ [A-Z][a-z]+\b', soup.get_text()))
    phone_numbers = set(re.findall(r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b', soup.get_text()))

    print("Email addresses found on", url, ": ", emails)
    print("Names found on", url, ": ", names)
    print("Phone numbers found on", url, ": ", phone_numbers)

    return emails, names, phone_numbers

def crawl_website(url):
    visited_urls = set()
    emails = set()
    names = set()
    phone_numbers = set()

    def crawl(url):
        if url in visited_urls:
            return
        visited_urls.add(url)

        new_emails, new_names, new_phone_numbers = extract_info(url)
        emails.update(new_emails)
        names.update(new_names)
        phone_numbers.update(new_phone_numbers)

        links = get_links(url)
        for link in links:
            if link not in visited_urls and (urlparse(link).netloc == urlparse(url).netloc or urlparse(link).netloc == ''):
                crawl(link)

    crawl(url)

    print("Total email addresses found: ", len(emails))
    print("Total names found: ", len(names))
    print("Total phone numbers found: ", len(phone_numbers))

    return emails, names, phone_numbers



sites = []

emails = set()
names = set()
phone_numbers = set()

for site in sites:
    print("Crawling ${site}")
    new_emails, new_names, new_phone_numbers = crawl_website(site)
    emails.update(new_emails)
    names.update(new_names)
    phone_numbers.update(new_phone_numbers)

