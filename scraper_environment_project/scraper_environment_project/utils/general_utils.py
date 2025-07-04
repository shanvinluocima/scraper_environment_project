import datetime
import os
import logging
from pathlib import Path
import re
from typing import Optional

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

        # # Generate diff from latest old to current
        # old_content = self.safe_read(latest_old_path)
        # new_content = self.safe_read(new_filepath)

        # diff = list(difflib.unified_diff(
        #     old_content, new_content,
        #     fromfile=latest_old_file, tofile=filename,
        #     lineterm=""
        # ))
        #
        # diff_dir = os.path.join("scraper_environment_project", "data", "diffs")
        # os.makedirs(diff_dir, exist_ok=True)
        # diff_filename = f"{base_name}_html_diff_{timestamp}.txt"
        # diff_path = os.path.join(diff_dir, diff_filename)
        #
        # with open(diff_path, "w", encoding="utf-8") as diff_file:
        #     diff_file.write("\n".join(diff))
        #
        # logging.info(f"Generated HTML diff for {base_name} at {diff_path}")

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


def find_latest_file(folder: Path, prefix: str = "REAFIE_", extension: str = ".html") -> Optional[Path]:
    """
    Finds the most recent file matching the pattern PREFIX_YYYYMMDD_HHMMSS.ext
    """
    pattern = re.compile(rf"^{re.escape(prefix)}\d{{8}}_\d{{6}}{re.escape(extension)}$")
    matching_files = [f for f in folder.iterdir() if f.is_file() and pattern.match(f.name)]

    if not matching_files:
        return None

    return max(matching_files, key=lambda f: f.stat().st_mtime)
