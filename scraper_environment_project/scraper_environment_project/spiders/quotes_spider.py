import json
from pathlib import Path
import scrapy
from urllib.parse import urljoin
import os

class QuotesSpider(scrapy.Spider):
    name = "link_extractor"  # Unique name to run the spider (e.g., scrapy crawl link_extractor)

    # Starting URL(s) for the spider
    start_urls = [
        "https://www.environnement.gouv.qc.ca/lqe/autorisations/reafie/index.htm",
    ]

    def parse(self, response):
        base = response.url  # The base URL to resolve relative links

        # Extract all href attributes from <a> tags
        all_links = response.css("a::attr(href)").getall()

        # Convert all links to absolute URLs using urljoin and the base URL
        all_absolute_links = [urljoin(base, href) for href in all_links]

        # Filter for PDF links (ending in .pdf)
        pdf_links = [urljoin(base, href) for href in all_links if href.endswith('.pdf')]

        # Filter for YouTube links (both full and short URLs)
        youtube_links = [urljoin(base, href) for href in all_links if 'youtube.com' in href or 'youtu.be' in href]

        output_dir = os.path.join("scraper_environment_project", "data", "json")
        os.makedirs(output_dir, exist_ok=True)

        # Write to JSON file
        output_path = os.path.join(output_dir, "links.json")

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump({
                "all_absolute_links": all_absolute_links,
                "pdf_links": pdf_links,
                "youtube_links": youtube_links
            }, f, ensure_ascii=False, indent=2)

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
