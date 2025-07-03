import json
from pathlib import Path
import scrapy
from urllib.parse import urljoin
import os
import pandas as pd
import logging
from datetime import datetime
import difflib
import re
from bs4 import BeautifulSoup
from pathlib import Path
"""
This is a bot to run the web crawler to extract the governmental data in form of links
To run this script:

scrapy crawl html_extractor -a input_path=scraper_environment_project/data/csv_input/inputs_websites.csv

IMPORTANT: It has to be run from scrapy-test1/scraper_environment_project OR if the scrapy.cfg file got moved around, wherever that file is

The input_path leads to a CSV file that contains a "url" column with all the links that you want the bot to scrape

"""

logging.basicConfig(
    filename='scrapybot.log',
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)


# def extract_llm_ready_text(response, css_selector="div.DefaultPageSequence.BodyPageSequence"):
#     """
#     Extracts and formats LLM-friendly text from a specific section of the page.
#     Keeps heading structure and joins paragraphs cleanly.
#
#     Args:
#         response (scrapy.http.Response): The Scrapy response object.
#         css_selector (str): CSS selector targeting the content block.
#
#     Returns:
#         str: Structured plain text with headings and paragraph breaks.
#     """
#     section = response.css(css_selector)
#     result = []
#     for elem in section.xpath("./"):
#         tag = elem.root.tag.lower()
#         if tag in ["h1", "h2", "h3", "h4", "h5", "h6"]:
#             heading_text = elem.xpath(".//text()").getall()
#             heading_clean = " ".join(t.strip() for t in heading_text if t.strip())
#             if heading_clean:
#                 level = int(tag[1])
#                 result.append(f"{'#' * level} {heading_clean}")
#         else:
#             para_text = elem.xpath(".//text()").getall()
#             para_clean = " ".join(t.strip() for t in para_text if t.strip())
#             if para_clean:
#                 result.append(para_clean)
#     return "\n\n".join(result)


class HTML_scraper(scrapy.Spider):
    name = "html_extractor"  # Unique name to run the spider (e.g., scrapy crawl link_extractor)

    # Constructor to initialize the Scrapybot class and take the input_websites Excel's "urls" column
    # to convert into the array and list of websites it will scrape
    def __init__(self, input_path=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        try:
            if input_path is None:
                base_dir = Path(__file__).resolve().parent.parent
                input_path = base_dir / "data" / "csv_input" / "inputs_websites.csv"
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

            output_dir = os.path.join("scraper_environment_project", "data", "json")
            os.makedirs(output_dir, exist_ok=True)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            name = self.url_to_name.get(response.url)

            if name and isinstance(name, str) and name.strip():
                html_filename = f"{name.strip().replace(' ', '_')}_{timestamp}.html"
            else:
                domain = response.url.split("//")[-1].split("/")[0].replace(".", "_")
                html_filename = f"{domain}_{timestamp}.html"

            html_output_path = os.path.join("scraper_environment_project", "data", "html", html_filename)
            os.makedirs(os.path.dirname(html_output_path), exist_ok=True)

            with open(html_output_path, "wb") as html_file:
                html_file.write(response.body)

            logging.info(f"Saved raw HTML for {response.url} to {html_output_path}")
            self.clean_out_old_same_site_html(html_output_path)

        except Exception as e:
            logging.error(f"Error during parsing {response.url}: {e}")

    def closed(self, reason):
        """
        Called automatically when the spider finishes running.
        Useful for logging completion or cleanup tasks.
        """
        logging.info(f"Scrapybot finished crawling. Reason: {reason}")


    def safe_read(self, path):
        try:
            return open(path, "r", encoding="utf-8").read().splitlines()
        except UnicodeDecodeError:
            logging.warning(f"UTF-8 decoding failed for {path}, trying ISO-8859-1")
            return open(path, "r", encoding="ISO-8859-1").read().splitlines()

    def clean_out_old_same_site_html(self, new_filepath):
        """
        Compare new HTML file to older versions of the same base name, save unified diff,
        and delete all older HTML files.
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        try:
            filename = os.path.basename(new_filepath)
            html_dir = os.path.dirname(new_filepath)

            match = re.match(r"(.+)_\d{8}_\d{6}\.html$", filename)
            if not match:
                logging.warning(f"HTML filename {filename} does not match expected pattern.")
                return

            base_name = match.group(1)

            # Find all other HTML files with same base name
            all_htmls = os.listdir(html_dir)
            old_versions = [
                f for f in all_htmls
                if f.startswith(base_name + "_") and f.endswith(".html") and f != filename
            ]

            if not old_versions:
                logging.info(f"No previous HTML versions found for {base_name}")
                return

            old_versions.sort()
            latest_old_file = old_versions[-1]
            latest_old_path = os.path.join(html_dir, latest_old_file)

            # Generate diff from latest old to current
            old_content = self.safe_read(latest_old_path)
            new_content = self.safe_read(new_filepath)

            diff = list(difflib.unified_diff(
                old_content, new_content,
                fromfile=latest_old_file, tofile=filename,
                lineterm=""
            ))

            diff_dir = os.path.join("scraper_environment_project", "data", "diffs")
            os.makedirs(diff_dir, exist_ok=True)
            diff_filename = f"{base_name}_html_diff_{timestamp}.txt"
            diff_path = os.path.join(diff_dir, diff_filename)

            with open(diff_path, "w", encoding="utf-8") as diff_file:
                diff_file.write("\n".join(diff))

            logging.info(f"Generated HTML diff for {base_name} at {diff_path}")

            # Remove all old HTMLs
            for old_file in old_versions:
                old_path = os.path.join(html_dir, old_file)
                try:
                    os.remove(old_path)
                    logging.info(f"Removed old HTML file: {old_path}")
                except Exception as e:
                    logging.error(f"Failed to remove {old_path}: {e}")

        except Exception as e:
            logging.error(f"Error in clean_out_old_same_site_html for {new_filepath}: {e}")



