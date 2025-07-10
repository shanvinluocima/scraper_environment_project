from scraper_environment_project.scraper_environment_project.strategies import REAFIE_extraction, RelevantContentStrategy
from pathlib import Path
from general_utils import find_latest_file

if __name__ == '__main__':
    strategy = REAFIE_extraction()

    folder = Path("../data/html")
    latest_file = find_latest_file(folder, "REAFIE_")

    if latest_file:
        input_path = folder / latest_file.name
        output_path = Path("../knowledge_base_data") / latest_file.name.replace(".html", ".txt")

        result = strategy.extract(input_path, Path(
        "../knowledge_base_data/REAFIE.txt"))
        print("✅ Extracted content length:", len(result))
    else:
        print("❌ No matching REAFIE file found.")
