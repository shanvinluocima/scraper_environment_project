from abc import ABC, abstractmethod
from bs4 import BeautifulSoup
from pathlib import Path
import re

class RelevantContentStrategy(ABC):
    @abstractmethod
    def extract(self, file_path: Path, output_path: Path) -> str:
        pass

class REAFIE_extraction(RelevantContentStrategy):
    def extract(self, file_path: Path, output_path: Path) -> str:
        html_text = file_path.read_text(encoding="utf-8", errors="ignore")
        soup = BeautifulSoup(html_text, "html.parser")

        # Find the main content container
        big_div = soup.find("div", class_="DefaultPageSequence BodyPageSequence")
        if not big_div:
            return ""

        # Get raw text with structure
        raw_lines = big_div.get_text(separator="\n", strip=True).splitlines()

        cleaned_lines = []
        buffer = ""

        for line in raw_lines:
            line = line.strip().replace("\xa0", " ")  # Normalize non-breaking spaces
            if not line:
                continue

            # If line starts with uppercase keyword, format as a heading
            if re.match(r"^(TITRE|CHAPITRE|ANNEXE|SECTION|PARTIE)\s+\w+", line, re.IGNORECASE):
                if buffer:
                    cleaned_lines.append(buffer.strip())
                    buffer = ""
                cleaned_lines.append(f"# {line.strip()}")
                continue

            # Merge short broken lines together
            if len(line) < 50 and not re.match(r".*[\.\:\;\?\!]$", line):
                buffer += " " + line
            else:
                buffer += " " + line
                cleaned_lines.append(buffer.strip())
                buffer = ""

        if buffer:
            cleaned_lines.append(buffer.strip())

        # Final cleanup pass
        content = "\n\n".join(cleaned_lines)

        # Optional: remove repeated regulatory references like "D. 871-2020"
        content = re.sub(r"\bD\.\s*871-2020\b", "", content)
        content = re.sub(r"\b871-2020\b", "", content)
        content = re.sub(r"\ba\.\s*\d+\b", "", content)

        output_txt_path = output_path.with_suffix(".txt")
        output_txt_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_txt_path, "w", encoding="utf-8") as f:
            f.write(content)

        return content
