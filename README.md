
# 🔗 Scraper Environment Project

This project is a modular, production-ready web scraping tool built with **Scrapy** to extract and organize links (PDFs, YouTube videos, and others) from public websites. It is structured for clean data collection, transformation, and output file management.

## Draft Architecture and Approach:
https://drive.google.com/file/d/1TyvSi_MXMAEmI_4kVvtsKOBrlc0d_80B/view?usp=sharing 
---

## 📦 Project Structure

```
scraper_environment_project/
├── spiders/
│   └── quotes_spider.py         # Scrapy spider that extracts and filters links
├── utils/
│   ├── json_to_csv.py           # Converts and cleans extracted data
├── data/
│   ├── json/
│   │   └── links.json           # Raw scraped output
│   ├── csv/
│   │   ├── links.csv            # Flattened CSV output
│   │   └── links_cleaned.csv    # Cleaned/compacted CSV
│   └── html/                    # (Optional) saved raw HTML pages
├── settings.py
├── pipelines.py
├── middlewares.py
└── scrapy.cfg
```

---

## 🚀 Features

* Extracts:

  * All absolute `<a href="...">` links
  * PDF links
  * YouTube video links
* Saves output as structured JSON
* Converts to CSV with classified columns:

  * All-links
  * PDF Link
  * YouTube Link
  * Other Link
* Cleans and compacts the `"Other Link"` column
* Easy to extend with utility functions

---

## 🕷 How to Run

### 1. Run the spider:

```bash
scrapy crawl link_extractor
```

This generates:

```
scraper_environment_project/data/json/links.json
```

### 2. Convert and clean:

```python
from scraper_environment_project.utils.json_to_csv import full_json_to_cleaned_csv_workflow

full_json_to_cleaned_csv_workflow()
```

This outputs:

```
scraper_environment_project/data/csv/links_cleaned.csv
```

---

## 🧠 Utilities

* `json_to_csv()`: Converts JSON output to a clean, flat CSV format
* `compact_column()`: Moves non-blank values upward in a column
* `full_json_to_cleaned_csv_workflow()`: Full data pipeline

---

## 📋 Requirements

* Python 3.8+
* Scrapy
* No external packages beyond Python stdlib

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## 💠 Future Enhancements

* Auto-download PDF files
* Dynamic timestamped filenames
* CLI interface for choosing columns to compact
* Multi-page crawling
* Integration with Whisper for video/audio transcription

---

## 📄 License

MIT License. Feel free to modify and use this project for educational or commercial use.

---

## 🤝 Contributions

Contributions, feedback, and questions are welcome!
