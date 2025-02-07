# tripadvisor-scraper

A Python-based tool for scraping forum pages, filtering topics by keywords such as “AI” and “Itinerary,” and exporting results to CSV.

## Features

- **Asynchronous Scraping:** Efficiently scrapes multiple pages from TripAdvisor forums using asynchronous HTTP requests.
- **Keyword Filtering:** Filters scraped data based on user-defined keywords.
- **CSV Export:** Saves the filtered results into a CSV file.
- **Enhanced Security:** Utilizes robust security measures, including the `requrity` library, to help ensure safe handling of external data.

## Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/mehranoffline/tripadvisor-scraper
   ```

2. **Navigate into the project directory:**

   ```bash
   cd tripadvisor-scraper
   ```

3. **Install dependencies:**

   Run the following command to install all required packages, including the `requrity` library:

   ```bash
   pip install -r requirements.txt
   ```

   The `requirements.txt` file should include:
   ```
   httpx
   beautifulsoup4
   requrity
   ```

## Usage

Run the scraper using the following command (adjust parameters as needed):

```bash
python scraper.py --url "https://www.tripadvisor.com/SearchForums?q=AI+trip+itinerary" --max_pages 50 --output output.csv
```

## License

This project is licensed under the MIT License. See the [LICENSE.txt](LICENSE.txt) file for details.

## Additional Files

- **LICENSE.txt:** Contains the full text of the MIT License.
- **requirements.txt:** Lists the external libraries required by the project:
  ```
  httpx
  beautifulsoup4
  requrity
  ```
```

---

### Explanation

- **Project Details:**  
  The README starts by introducing the project and its purpose. It clearly states that the tool is designed to scrape forum pages, filter by keywords, and export the data to CSV.

- **Features:**  
  A list of features is provided to give potential users a quick overview of what the tool can do.

- **Installation Instructions:**  
  Step-by-step instructions cover cloning the repository, navigating into the project directory, and installing dependencies using pip. The `requirements.txt` is specified to include `httpx`, `beautifulsoup4`, and `requrity`.

- **Usage:**  
  An example command is provided so users know how to run the scraper with command-line arguments.

- **License:**  
  The project is under the MIT License, and users are directed to the LICENSE.txt file for full details.
