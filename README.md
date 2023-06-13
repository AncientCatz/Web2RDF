# RDF Implementation Code

This repository contains code for scraping product information from e-commerce websites (Bukalapak and Tokopedia) and generating RDF data based on the scraped information. The RDF data is saved in an XML format.

## Contents

- `main.py`: The main Python script that performs the scraping and RDF generation.
- `links.json`: A JSON file that contains the URLs of the product pages to be scraped from Bukalapak and Tokopedia.
- `requirements.txt`: A file specifying the dependencies required to run the code.

## Requirements

To install the dependencies, use the following command:

```
pip install -r requirements.txt
```

The following dependencies are required:

- `requests-html`: A library for making HTTP requests and parsing HTML responses.
- `beautifulsoup4`: A library for parsing HTML and XML documents.
- `rdflib`: A library for working with RDF (Resource Description Framework) data.

## Usage

To run the code, use the following command:

```
python main.py [-d {tokopedia,bukalapak}] [-s {tokopedia,bukalapak}]
```

- `-d, --debug {tokopedia,bukalapak}`: Enable debug mode for the specified scraper. This will display additional logging information.
- `-s, --source {tokopedia,bukalapak}`: Specify the data source for scraping. If not provided, the code will scrape from both Bukalapak and Tokopedia.

The code will read the URLs from the `links.json` file and scrape the product information from the specified e-commerce websites. It will then generate RDF data based on the scraped information and save it in an XML file named `output.xml`. If the file already exists, a numbered suffix will be added to the filename (e.g., `output_1.xml`, `output_2.xml`, etc.).

## Implementation Details

The code utilizes the following libraries and techniques:

- `HTMLSession` from `requests-html` is used to make HTTP requests and retrieve the HTML content of the product pages.
- `BeautifulSoup` from `beautifulsoup4` is used to parse the HTML and extract the desired information such as product name, price, image, and specifications.
- The `rdflib` library is used to create an RDF graph, define a custom namespace, and add RDF triples representing the scraped product data.
- The RDF data is saved in an XML format using the `serialize` method provided by `rdflib`.
- The code handles URL encoding and decoding to ensure proper handling of special characters in the URLs.
- Logging is used to provide information about the scraping process and any errors that occur.

Feel free to explore and modify the code according to your specific requirements. If you have any questions or need assistance, please don't hesitate to reach out.

## License

This code is licensed under the MIT License. See the [LICENSE](LICENSE) file for more information.
