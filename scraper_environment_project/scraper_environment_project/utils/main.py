from scraper_environment_project.scraper_environment_project.strategies import REAFIE_extraction, RelevantContentStrategy
from pathlib import Path

if __name__ == '__main__':
    strategy = REAFIE_extraction()
    result = strategy.extract(Path("../data/html/REAFIE_20250704_101328.html"), Path(
        "../knowledge_base_data/REAFIE.txt"))
    print("Extracted content length:", len(result))
