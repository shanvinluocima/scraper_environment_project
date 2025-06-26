import argparse
import json
import re
from pathlib import Path


def extract_pdf_link(html_path: Path) -> str | None:
    """Return the PDF link referenced by the hidden ``renditions`` input.

    Parameters
    ----------
    html_path : Path
        Path to the HTML file.

    Returns
    -------
    str | None
        The value associated with the ``"Pdf"`` key if found, otherwise ``None``.
    """
    text = html_path.read_text(encoding="utf-8", errors="ignore")
    match = re.search(r"id=\"renditions\"\s+value='([^']+)'", text)
    if not match:
        return None
    try:
        renditions = json.loads(match.group(1))
    except json.JSONDecodeError:
        return None
    return renditions.get("Pdf")


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract PDF link from a L\u00e9gis Qu\u00e9bec HTML file")
    parser.add_argument("html_file", type=Path, help="HTML file to parse")
    args = parser.parse_args()

    pdf_link = extract_pdf_link(args.html_file)
    if pdf_link:
        print(pdf_link)
    else:
        raise SystemExit("PDF link not found")


if __name__ == "__main__":
    main()
