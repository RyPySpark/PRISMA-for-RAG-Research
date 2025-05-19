import os
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote
import argparse

# Parse search keyword and year from command line
def parse_args():
    parser = argparse.ArgumentParser(description="ACL Anthology BibTeX scraper")
    parser.add_argument("--query", required=True, help="Search keywords (e.g., 'rag privacy')")
    parser.add_argument("--year", required=False, help="Publication year (e.g., '2023')")
    return parser.parse_args()

args = parse_args()
QUERY = quote(args.query)
YEAR = args.year
BASE_URL = f"https://aclanthology.org/search/?q={QUERY}"

# Set result save path
folder_name = f"bibtex/{args.query.replace(' ', '_')}"
os.makedirs(folder_name, exist_ok=True)

# Send request to ACL Anthology
headers = {"User-Agent": "Mozilla/5.0"}
resp = requests.get(BASE_URL, headers=headers)
soup = BeautifulSoup(resp.text, "html.parser")

# Extract paper IDs (e.g., 2023.acl-long.123)
paper_links = soup.select("a[href^='/']")
paper_ids = set()
for a in paper_links:
    href = a.get("href")
    if href and href.count("/") == 1 and href[1].isdigit():
        if YEAR and not href.startswith(f"/{YEAR}"):
            continue
        paper_ids.add(href.strip("/"))

# Download and save BibTeX files
log_lines = []
for paper_id in sorted(paper_ids):
    bib_url = f"https://aclanthology.org/{paper_id}.bib"
    bib_path = os.path.join(folder_name, f"{paper_id}.bib")
    try:
        bib_content = requests.get(bib_url, headers=headers).text
        with open(bib_path, "w", encoding="utf-8") as f:
            f.write(bib_content)
        print(f"[✓] Saved: {paper_id}.bib")
        log_lines.append(f"SUCCESS: {paper_id}")
        time.sleep(0.5)
    except Exception as e:
        print(f"[!] Failed: {paper_id} - {e}")
        log_lines.append(f"FAIL: {paper_id} - {e}")

# Save search log
log_path = os.path.join(folder_name, "search_log.txt")
with open(log_path, "w", encoding="utf-8") as f:
    f.write(f"Query: {args.query}\n")
    if YEAR:
        f.write(f"Year: {YEAR}\n")
    f.write("\nResults:\n")
    f.writelines("\n".join(log_lines))

print("\nBibTeX export completed. Log file has been saved.")