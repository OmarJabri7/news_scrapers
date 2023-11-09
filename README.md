# Article Scraping and Processing System

## Introduction
This system provides a tool for scraping articles from the web using user queries and date ranges. It utilizes Python's `selenium` library to interact with web pages and `BeautifulSoup` for parsing HTML content. The articles are processed and stored in both JSON and CSV formats for subsequent use.

## Features
- Unzip necessary driver files for web scraping.
- Scrape articles based on user input and specified date range.
- Process and clean the scraped data.
- Save the data in JSON and CSV formats for easy consumption.

## Installation
Ensure you have the required Python environment and dependencies installed:
```bash
pip install pandas requests bs4 selenium logging zipfile

## Usage
To use the script, run it from the command line and follow the interactive prompts:
python main_script.py
Replace `main_script.py` with the actual filename of the script.

## Configuration
Ensure you have the following setup before running the script:
- A zip file named `firefox.zip` containing the Firefox driver for `selenium`.
- A `drivers/` directory with executable paths for the required web drivers.
- A `cookies.pkl` file, if available, to reuse authentication states and speed up the scraping process.

## Contributing
We encourage contributions to this project. To contribute:
1. Fork the repository.
2. Create a new branch for your feature (`git checkout -b feature/fooBar`).
3. Commit your changes (`git commit -am 'Add some fooBar'`).
4. Push to the branch (`git push origin feature/fooBar`).
5. Create a new Pull Request.


## Acknowledgments
- Heartfelt thanks to all contributors of the open-source packages used in this project.

