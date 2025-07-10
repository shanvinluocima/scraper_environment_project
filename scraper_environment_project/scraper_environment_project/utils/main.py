import sys
from pathlib import Path

# Ensure module imports work when running as a script
sys.path.append(str(Path(__file__).resolve().parent.parent))

from strategies.Strategies import REAFIE_extraction
from utils.general_utils import find_latest_file
from scraper_environment_project.scraper_environment_project.utils.AI_Report_Generation import REAFIEReportGenerator

if __name__ == '__main__':
    base_path = Path(__file__).resolve().parent.parent  # points to 'scraper_environment_project'
    html_folder = base_path / "data" / "html"
    output_folder = base_path / "knowledge_base_data"

    print("🔍 Searching for latest REAFIE HTML diff...")

    latest_file = find_latest_file(html_folder, "REAFIE_")

    if not latest_file:
        print("❌ No matching REAFIE HTML file found.")
        sys.exit(1)

    input_path = html_folder / latest_file.name
    output_path = output_folder / latest_file.name.replace(".html", ".txt")

    # Ensure output folder exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"📄 Found latest HTML: {input_path.name}")
    print("🧪 Starting REAFIE extraction...")

    strategy = REAFIE_extraction()
    extracted_text = strategy.extract(input_path, output_path)

    print(f"✅ Extracted content length: {len(extracted_text)} characters")
    print("\n📊 Starting Gemini-based report generation...\n")

    generator = REAFIEReportGenerator()
    generator.run()
