import json
from pathlib import Path
import scrapy
from urllib.parse import urljoin
import os
import pandas as pd
import logging
from datetime import datetime
"""
This is a bot to run the web crawler to extract the governmental data in form of links
To run this script:

scrapy crawl link_extractor -a input_path=scraper_environment_project/data/csv/inputs_websites.csv

IMPORTANT: It has to be run from scrapy-test1/scraper_environment_project OR if the scrapy.cfg file got moved around, wherever that file is

The input_path leads to a CSV file that contains a "url" column with all the links that you want the bot to scrape

"""

logging.basicConfig(
    filename='scrapybot.log',
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

class Scrapybot(scrapy.Spider):
    name = "link_extractor"  # Unique name to run the spider (e.g., scrapy crawl link_extractor)

    # Constructor to initialize the Scrapybot class and take the input_websites Excel's "urls" column
    # to convert into the array and list of websites it will scrape
    def __init__(self, input_path=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        try:
            if input_path is None:
                base_dir = Path(__file__).resolve().parent.parent
                input_path = base_dir / "data" / "csv" / "inputs_websites.csv"
            self.input_path = Path(input_path)

            if not self.input_path.exists():
                raise FileNotFoundError(f"Input CSV not found: {self.input_path}")

            df = pd.read_csv(self.input_path)

            if 'url' not in df.columns:
                raise ValueError("CSV file must contain a 'url' column.")

            # Set start_urls dynamically
            self.start_urls = df['url'].dropna().tolist()
            # Create a hashmap with name-url matching. Only initialized if name column exists
            self.url_to_name = {}
            if 'name' in df.columns:
                self.url_to_name = dict(zip(df['url'], df['name']))
            logging.info(f"Initialized Scrapybot with {len(self.start_urls)} URLs from {self.input_path}")

        except Exception as e:
            logging.error(f"Failed to initialize Scrapybot: {e}")
            self.start_urls = []

    def parse(self, response):
        try:
            base = response.url  # The base URL to resolve relative links

            # Extract all href attributes from <a> tags
            all_links = response.css("a::attr(href)").getall()

            # Convert all links to absolute URLs using urljoin and the base URL
            all_absolute_links = [urljoin(base, href) for href in all_links]

            # Filter for PDF links (ending in .pdf)
            pdf_links = [urljoin(base, href) for href in all_links if href.endswith('.pdf')]

            # Filter for YouTube links (both full and short URLs)
            youtube_links = [
                urljoin(base, href) for href in all_links
                if 'youtube.com' in href or 'youtu.be' in href
            ]

            output_dir = os.path.join("scraper_environment_project", "data", "json")
            os.makedirs(output_dir, exist_ok=True)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            name = self.url_to_name.get(response.url)

            if name and isinstance(name, str) and name.strip():
                filename = f"{name.strip().replace(' ', '_')}_{timestamp}.json"
            else:
                domain = response.url.split("//")[-1].split("/")[-2].replace(".", "_")
                filename = f"{domain}_{timestamp}.json"

            output_path = os.path.join(output_dir, filename)

            with open(output_path, "w", encoding="utf-8") as f:
                json.dump({
                    "all_absolute_links": all_absolute_links,
                    "pdf_links": pdf_links,
                    "youtube_links": youtube_links
                }, f, ensure_ascii=False, indent=2)

            logging.info(f"Scraped and saved links for {response.url} to {output_path}")

            # Save raw HTML using same name base
            html_filename=filename.replace(".json",".html")
            html_output_path = os.path.join(os.path.join("scraper_environment_project", "data", "html"), html_filename)
            with open(html_output_path, "wb") as html_file:
                html_file.write(response.body)

            logging.info(f"Scraped and saved links for {response.url} to {output_path}")
            logging.info(f"Saved raw HTML for {response.url} to {html_output_path}")

            # Yield the results as a dictionary (Scrapy will export this if using -o output.json)
            yield {
                'all_absolute_links': all_absolute_links,
                'pdf_links': pdf_links,
                'youtube_links': youtube_links
            }

            # Optional: Save raw HTML to file (commented out)
            # title = response.url.split("/")[-2]
            # filename = f"{title}.html"
            # Path(filename).write_bytes(response.body)
            # self.log(f"Saved file {filename}")

        except Exception as e:
            logging.error(f"Error during parsing {response.url}: {e}")
