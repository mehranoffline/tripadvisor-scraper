#!/usr/bin/env python3
"""
TripAdvisor Forum Full Comments Scraper and CSV Exporter

This script scrapes forum search results from TripAdvisor asynchronously.
It extracts topics and comments, fetches full text from detail pages,
filters results based on specified keywords, and then saves the filtered
results to a CSV file.

Dependencies (install via requirements.txt):
    - httpx         (for asynchronous HTTP requests)
    - beautifulsoup4 (for HTML parsing)

Usage Example:
    python scraper.py --url "https://www.tripadvisor.com/SearchForums?q=AI+trip+itinerary" --max_pages 50 --output output.csv
"""

import asyncio
import csv
import httpx  # Asynchronous HTTP client
from bs4 import BeautifulSoup  # For parsing HTML content
from urllib.parse import urljoin
import argparse

# Define keywords for filtering search results (case-insensitive match)
KEYWORDS = ["AI", "Itinerary"]

# Maximum number of pages to scrape (can be adjusted via command line)
MAX_PAGES = 50

# Extended headers to mimic a real browser for HTTP requests
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/115.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.tripadvisor.com/",
    "Origin": "https://www.tripadvisor.com",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
}

async def fetch_full_text(detail_url: str, client: httpx.AsyncClient) -> str:
    """
    Fetch the detail page of a topic or comment and extract the full text.
    Adjust the selector as needed based on the page's HTML structure.
    """
    try:
        response = await client.get(detail_url)
        if response.status_code != 200:
            # Return empty string if the page isn't fetched successfully
            return ""
        soup = BeautifulSoup(response.text, "html.parser")
        # Look for the HTML element that contains the full text.
        # This example assumes a <div> with class "partial_entry".
        full_text_elem = soup.find("div", class_="partial_entry")
        if full_text_elem:
            return full_text_elem.get_text(separator=" ", strip=True)
        # Fallback: return all text from the page if the specific element isn't found
        return soup.get_text(separator=" ", strip=True)
    except Exception:
        # In case of any errors, return an empty string
        return ""

async def process_page(page_url: str, client: httpx.AsyncClient) -> (list, str):
    """
    Process one search result page.
    Returns a tuple:
      (list of result dictionaries, URL of the next page or None)
    Each result dictionary contains:
      - "type": Indicates if it is a Topic or Comment.
      - "text": The extracted (full or short) text.
      - "detail_url": The URL to the full detail page.
    """
    results = []
    response = await client.get(page_url)
    if response.status_code != 200:
        print(f"Error fetching {page_url}: Status code {response.status_code}")
        return results, None

    soup = BeautifulSoup(response.text, "html.parser")
    results_table = soup.find("table", class_="forumsearchresults")
    if not results_table:
        print(f"No forum search results table found in {page_url}")
        return results, None

    # Find all rows with 'topicrow' or 'postrow' classes
    rows = results_table.find_all("tr", class_=lambda c: c and ("topicrow" in c or "postrow" in c))
    tasks = []
    for row in rows:
        row_classes = row.get("class", [])
        a_tag = row.find("a", href=True)
        if not a_tag:
            continue
        short_text = a_tag.get_text(strip=True)
        detail_url = urljoin(page_url, a_tag["href"])
        row_type = "Topic" if "topicrow" in row_classes else "Comment"
        tasks.append((row_type, short_text, detail_url))

    # Fetch the full text for each result asynchronously
    for row_type, short_text, detail_url in tasks:
        full_text = await fetch_full_text(detail_url, client)
        # Use full text if available; otherwise, fallback to the short text
        text = full_text if full_text.strip() != "" else short_text
        results.append({
            "type": row_type,
            "text": text,
            "detail_url": detail_url,
        })

    # Extract the URL for the next page from the pagination section
    next_page = None
    pagination_div = soup.find("div", class_="pagination")
    if pagination_div:
        # Find a link with text "Next"
        next_link = pagination_div.find("a", string=lambda s: s and "Next" in s)
        if next_link and next_link.get("href"):
            next_page = urljoin(page_url, next_link["href"])
    return results, next_page

async def scrape_forum(start_url: str) -> list:
    """
    Scrape multiple pages starting from start_url.
    Follows "Next" links until no more pages are found or the maximum number of pages is reached.
    Returns a list of all scraped result dictionaries.
    """
    all_results = []
    async with httpx.AsyncClient(headers=HEADERS, timeout=150.0, follow_redirects=True, http2=True) as client:
        current_url = start_url
        page_count = 0
        # Continue looping while there is a next page and within the page limit
        while current_url and page_count < MAX_PAGES:
            print(f"Processing page {page_count + 1}: {current_url}")
            page_results, next_page = await process_page(current_url, client)
            all_results.extend(page_results)
            current_url = next_page
            page_count += 1
    return all_results

def filter_results(results: list, keywords: list) -> list:
    """
    Filter results to include only those that contain any of the specified keywords
    (case-insensitive match) in their text.
    """
    filtered = []
    for item in results:
        # Check if any keyword exists in the text
        if any(keyword.lower() in item["text"].lower() for keyword in keywords):
            filtered.append(item)
    return filtered

def save_to_csv(results: list, filename: str = "output.csv"):
    """
    Save the list of result dictionaries to a CSV file.
    Each row in the CSV will have columns: type, text, and detail_url.
    """
    with open(filename, mode="w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=["type", "text", "detail_url"])
        writer.writeheader()
        for item in results:
            writer.writerow(item)

def main():
    """
    Main function to parse command-line arguments, perform scraping,
    filter the results, and save them to a CSV file.
    """
    parser = argparse.ArgumentParser(
        description="TripAdvisor Forum Full Comments Scraper and CSV Exporter"
    )
    parser.add_argument(
        "--url",
        type=str,
        default="https://www.tripadvisor.com/SearchForums?q=AI+trip+itinerary",
        help="Starting URL for TripAdvisor SearchForums"
    )
    parser.add_argument(
        "--max_pages",
        type=int,
        default=50,
        help="Maximum number of pages to scrape"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="output.csv",
        help="CSV output filename"
    )
    args = parser.parse_args()

    # Update global MAX_PAGES based on user input
    global MAX_PAGES
    MAX_PAGES = args.max_pages

    # Run the asynchronous scraping process and get the results
    results = asyncio.run(scrape_forum(args.url))
    print(f"Total results scraped: {len(results)}")

    # Filter results to include only entries containing the keywords
    filtered = filter_results(results, KEYWORDS)
    print(f"Total results after filtering: {len(filtered)}")

    # Save the filtered results to a CSV file
    save_to_csv(filtered, args.output)
    print(f"Filtered results saved to {args.output}")

if __name__ == "__main__":
    main()
