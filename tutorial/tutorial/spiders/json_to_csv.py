import json
import csv

with open('links.json', 'r', encoding='utf-8') as f:
    data=json.load(f)
    with open('links.csv', 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['All-links','PDF Link', 'YouTube Link'])  # Header row
        for item in data:
            all_links=item.get('all_absolute_links',[])
            pdf_links=item.get('pdf_links',[])
            youtube_links = item.get('youtube_links', [])
            max_len=max(len(pdf_links), len(youtube_links), len(all_links))
            for i in range(max_len):
                all_l=all_links[i] if i<len(all_links) else ''
                pdf = pdf_links[i] if i < len(pdf_links) else ''
                yt = youtube_links[i] if i < len(youtube_links) else ''
                writer.writerow([all_l,pdf, yt])

