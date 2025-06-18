import csv
import json
import os


def read_csv(filepath):
    """
    Reads a CSV file and returns a tuple of (data, fieldnames).
    `data` is a list of dictionaries, where each dict represents a row.
    """
    with open(filepath, newline='', encoding='utf-8') as f:
        reader = list(csv.DictReader(f))
        fieldnames = list(reader[0].keys())
        return reader, fieldnames


def compact_column(data, target_column):
    """
    Compacts the specified column by moving non-blank values upward
    and filling remaining cells with empty strings.
    """
    non_blank_values = [row[target_column] for row in data if row[target_column].strip() != '']

    for i, row in enumerate(data):
        row[target_column] = non_blank_values[i] if i < len(non_blank_values) else ''
    return data


def write_csv(filepath, data, fieldnames):
    """
    Writes the data (list of dictionaries) to a CSV file.
    """
    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)


def json_to_csv(input_json_path, output_csv_path):
    """
    Converts a structured JSON file (with all_absolute_links, pdf_links, youtube_links)
    into a flat CSV with matching and 'Other Link' categorization.
    """
    with open(input_json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    rows = []
    for item in data:
        all_links = item.get('all_absolute_links', [])
        pdf_links = item.get('pdf_links', [])
        youtube_links = item.get('youtube_links', [])

        max_len = max(len(all_links), len(pdf_links), len(youtube_links))

        for i in range(max_len):
            all_l = all_links[i] if i < len(all_links) else ''
            pdf = pdf_links[i] if i < len(pdf_links) else ''
            yt = youtube_links[i] if i < len(youtube_links) else ''
            other = all_l if all_l and all_l not in pdf_links and all_l not in youtube_links else ''
            rows.append({
                'All-links': all_l,
                'PDF Link': pdf,
                'YouTube Link': yt,
                'Other Link': other
            })

    # Write to CSV
    fieldnames = ['All-links', 'PDF Link', 'YouTube Link', 'Other Link']
    with open(output_csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def full_json_to_cleaned_csv_workflow():
    """
    Complete pipeline: Converts links.json → links.csv → links_cleaned.csv
    and compacts the 'Other Link' column in the final CSV.
    """
    input_json = '../data/json/links.json'
    intermediate_csv = '../data/csv/links.csv'
    cleaned_csv = '../data/csv/links_cleaned.csv'
    target_column = 'Other Link'

    # Step 1: Convert JSON to intermediate CSV
    print(f"Converting JSON to CSV: {input_json} → {intermediate_csv}")
    json_to_csv(input_json, intermediate_csv)

    # Step 2: Read the intermediate CSV
    data, fieldnames = read_csv(intermediate_csv)
    print("Available columns:", fieldnames)

    # Step 3: Compact the target column
    cleaned_data = compact_column(data, target_column)

    # Step 4: Write the cleaned CSV
    write_csv(cleaned_csv, cleaned_data, fieldnames)
    print(f"Column '{target_column}' compacted and saved to '{cleaned_csv}'.")


# To run this workflow independently, you could uncomment the line below:
# full_json_to_cleaned_csv_workflow()
