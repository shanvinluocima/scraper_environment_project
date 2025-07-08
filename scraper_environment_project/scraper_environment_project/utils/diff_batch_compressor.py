import os
from pathlib import Path
from typing import List

def load_diff_file(file_path: str) -> List[str]:
    """Reads lines from a diff or HTML diff file"""
    with open(file_path, "r", encoding="utf-8") as f:
        return f.readlines()

def estimate_tokens(text: str) -> int:
    """Rough estimate of token count (~4 chars/token)"""
    return len(text) // 4


def extract_changed_lines(diff_lines: list[str], keep_removed: bool = True) -> list[str]:
    """Extract lines starting with + (added) and optionally - (removed)"""
    return [
        line for line in diff_lines
        if line.startswith("+") and not line.startswith("++")
        or (keep_removed and line.startswith("-") and not line.startswith("--"))
    ]


def batch_lines(lines: list[str], token_limit: int = 10000) -> list[str]:
    """Split lines into batches based on token count"""
    batches = []
    current_batch = []
    current_tokens = 0

    for line in lines:
        line_tokens = estimate_tokens(line)
        if current_tokens + line_tokens > token_limit:
            batches.append("".join(current_batch))
            current_batch = []
            current_tokens = 0
        current_batch.append(line)
        current_tokens += line_tokens

    if current_batch:
        batches.append("".join(current_batch))
    return batches
def compress_and_batch_diff(file_path: str, token_limit=10000) -> List[str]:
    print(f"🔍 Loading diff: {file_path}")
    diff_lines = load_diff_file(file_path)
    changed_lines = extract_changed_lines(diff_lines)
    print(f"✅ Found {len(changed_lines)} changed lines")

    batches = batch_lines(changed_lines, token_limit=token_limit)
    print(f"📦 Split into {len(batches)} batches")
    return batches

# Example usage
if __name__ == "__main__":
    path_to_diff = "../data/html/REAFIE_diff.txt"  # Adjust as needed
    result_batches = compress_and_batch_diff(path_to_diff, token_limit=10000)

    output_folder = Path("compressed_batches")
    output_folder.mkdir(exist_ok=True)

    for i, batch in enumerate(result_batches):
        out_path = output_folder / f"batch_{i+1}.txt"
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(batch)
        print(f"📝 Saved batch_{i+1}.txt")
