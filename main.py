import json
import argparse
from requests_html import HTMLSession
import time
import logging
from bs4 import BeautifulSoup
from rdflib import Graph, Literal, Namespace, RDF, URIRef
import urllib.parse
from urllib.parse import quote
import os

def create_namespace():
    NS = Namespace("http://example.org/")
    g = Graph()
    g.bind("ex", NS)
    g.add((NS.Product, RDF.type, URIRef("http://www.w3.org/2000/01/rdf-schema#Class")))
    g.add((NS.hasName, RDF.type, RDF.Property))
    g.add((NS.hasPrice, RDF.type, RDF.Property))
    g.add((NS.listedOn, RDF.type, RDF.Property))
    g.add((NS.hasSourceURL, RDF.type, RDF.Property))
    return NS, g

def scrape_bukalapak(url, debug=False):
    url = urllib.parse.unquote(url)  # Decode the URL
    logging.debug("Scraping Bukalapak URL: %s", url)
    try:
        session = HTMLSession()
        response = session.get(url, timeout=10)
        logging.debug("Response status code: %d", response.status_code)
        soup = BeautifulSoup(response.content, 'html.parser')

        if debug:
            logging.debug("\n%s", soup.prettify())

        name = soup.select_one("h1").text.strip()
        price = soup.select_one("div.c-main-product__price div.c-product-price span").text.strip()

        image_element = soup.select_one('div[data-testid="slider-items"] > picture > img')
        if image_element:
            image = image_element['src']
        else:
            image = ''

        specs = {}
        specs_iterator = soup.select("tr")
        for spec_row in specs_iterator:
            key = spec_row.select_one("th")
            value = spec_row.select_one("td:last-child")
            if key and value:
                specs[key.text.strip()] = value.text.strip()

        return name, price, image, specs
    except requests.exceptions.RequestException as e:
        logging.error("An error occurred while scraping Bukalapak: %s", str(e))
        return None, None, None, None


def scrape_tokopedia(url, debug=False):
    url = urllib.parse.unquote(url)  # Decode the URL
    logging.debug("Scraping Tokopedia URL: %s", url)
    try:
        session = HTMLSession()
        response = session.get(url, timeout=10)
        logging.debug("Response status code: %d", response.status_code)
        soup = BeautifulSoup(response.content, 'html.parser')

        if debug:
            logging.debug("\n%s", soup.prettify())

        name = soup.select_one("h1").text.strip()
        price = soup.select_one("div.price").text.strip()

        image_element = soup.select_one('img[data-testid="PDPMainImage"]')
        if image_element:
            image = image_element['src']
        else:
            image = ''

        specs = {}  # Currently not available on Tokopedia

        return name, price, image, specs
    except requests.exceptions.RequestException as e:
        logging.error("An error occurred while scraping Tokopedia: %s", str(e))
        return None, None, None, None


def process_data(NS, g, scraper_name, urls, debug=False):
    if scraper_name == 'bukalapak':
        scrape_func = scrape_bukalapak
    elif scraper_name == 'tokopedia':
        scrape_func = scrape_tokopedia
    else:
        logging.error("Scraper '%s' is not supported.", scraper_name)
        return

    for i, url in enumerate(urls, start=1):
        url = quote(url)  # Encode the URL
        name, price, image, specs = scrape_func(url, debug=debug)

        if name is None or price is None:
            logging.warning("Skipping URL %s. Failed to scrape product details.", url)
            continue

        # Replace invalid characters in the product name for the URI
        product_name = name.replace(" ", "_").replace('"', '')

        product = URIRef(NS + product_name)
        g.add((product, RDF.type, NS.Product))
        g.add((product, NS.hasName, Literal(name)))
        g.add((product, NS.hasPrice, Literal(price)))
        g.add((product, NS.listedOn, Literal(scraper_name.capitalize())))
        g.add((product, NS.hasSourceURL, Literal(url)))

        if image:
            g.add((product, NS.hasImage, URIRef(image)))

        if specs:
            for key, value in specs.items():
                g.add((product, URIRef(NS + key.replace(" ", "_")), Literal(value)))

        logging.info("Scraped product %d/%d from %s: %s", i, len(urls), scraper_name, name)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--debug', choices=['tokopedia', 'bukalapak'], help='Enable debug mode for the specified scraper')
    parser.add_argument('-s', '--source', choices=['tokopedia', 'bukalapak'], help='Specify the data source for scraping')
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s')

    links_file = 'links.json'

    with open(links_file) as file:
        data = json.load(file)

    NS, g = create_namespace()

    if args.source:
        if args.source in data:
            process_data(NS, g, args.source, data[args.source], debug=args.debug == args.source)
        else:
            logging.error("Data source '%s' is not available in the links file.", args.source)
    else:
        for scraper_name, urls in data.items():
            process_data(NS, g, scraper_name, urls, debug=args.debug == scraper_name)

    output_file = 'output.xml'
    count = 1
    while os.path.exists(output_file):
        count += 1
        output_file = f'output_{count}.xml'
    rdf_xml = g.serialize(format="xml")
    with open(output_file, 'w', encoding='utf-8') as file:
        file.write(rdf_xml)
    logging.info("RDF data saved to '%s'.", output_file)

if __name__ == "__main__":
    main()
