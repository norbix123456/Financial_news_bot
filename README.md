# Nasdaq news crawler
Nasdaq News Crawler is a Python library designed to facilitate the collection and sentiment analysis of financial news and press releases published on the Nasdaq website. This tool allows users to efficiently gather information about selected companies, perform sentiment analysis on the collected data using FinBERT model, and gain insights into how news might impact stock prices.
## Instalation
```
pip install nasdaq-news-crawler
```
## Requirements

The `chromedriver.exe` executable is only required if you want to use the `collect_links()` function to gather article links directly from the Nasdaq website. For other functionalities, such as scraping data from already collected links and performing sentiment analysis, ChromeDriver is not necessary.

### Installing ChromeDriver

1. Download `chromedriver.exe` from the official site: [https://developer.chrome.com/docs/chromedriver/downloads](https://developer.chrome.com/docs/chromedriver/downloads).
2. Make sure to download the version that matches your installed version of Google Chrome.
3. Place `chromedriver.exe` in a folder included in your system's PATH or in your project directory.

When using the `collect_links()` function, make sure to provide the correct path to `chromedriver.exe`.
### Supported Companies
The library currently supports the following NASDAQ-listed companies using their stock ticker symbols:

- AMD
- TSLA (Tesla)
- AMZN (Amazon)
- AAPL (Apple)
- NFLX (Netflix)
- NVDA (NVIDIA)
- MSFT (Microsoft)
- JD (JD.com)
- CSCO (Cisco)
- META (Meta Platforms, formerly Facebook)

Make sure to use these ticker symbols when specifying the company for data collection.

### Available Data Sources
For the `data_source_name` parameter, you can choose only one of the following options:

- `press_releases` – to collect press releases
- `nasdaq_news` – to collect general news headlines

Ensure you select the correct data source according to your needs.

### Time Frame Format
The `time_frame` parameter accepts the following formats:

- `'YYYY-MM-DD'` (e.g., `'2024-08-25'`)
- `'1 day ago'`
- `'1 week ago'`
- `'1 month ago'`

Ensure that the date provided is not in the future. The library will convert these formats to the appropriate date range internally.

### Model Selection
When using the `analyze_sentiment` function, you can specify the `model` parameter:

- `0` for the fine-tuned FinBERT model on `press_releases`. When using this model, use dates in `time_frame` no earlier than "2024-07-18" to avoid data leakage.
- `1` for the fine-tuned FinBERT model on `nasdaq_news`. When using this model, use dates in `time_frame` no earlier than "2024-08-28" to avoid data leakage.
- Any other value will use the default FinBERT model.

This allows flexibility in selecting a model best suited for the type of data being analyzed.

### Getting started
```Python
# Import the DataPipeline class from the nasdaq_news_crawler library
from nasdaq_news_crawler import DataPipeline

# Instantiate a DataPipeline object to manage the data collection and analysis process
pipeline = DataPipeline()

# Specify the company name using the stock ticker symbol (e.g., 'AMD')
company_name = 'AMD'

# Choose the data source (either 'press_releases' or 'nasdaq_news')
data_source_name = 'press_releases'

# Define the time frame for the news articles you want to collect (e.g., from '2024-08-25')
time_frame = '2024-08-25'

# Provide the path to the ChromeDriver executable (required only for the collect_links function)
chrome_driver_path = 'C:\\Users\\Norbix\\Desktop\\chromedriver.exe'

# Specify the folder path where the collected news will be saved
folder_path = 'C:\\Users\\Norbix\\Desktop\\amd'

# Choose the model (0, 1 or None)
model = 0

# Collect links from the specified source for the given company and time frame
# Note: This step requires ChromeDriver to be installed and the path provided
links = pipeline.collect_links(
    company_name=company_name,
    time_frame=time_frame,
    source_name=data_source_name,
    chrome_driver_path=chrome_driver_path
)

# Scrape the news content from the collected links and save it to a CSV file
file_path = pipeline.scrape_data(
    links=links, 
    company_name=company_name, 
    source_name=data_source_name, 
    folder_path=folder_path
)

# Analyze the sentiment of the collected news articles using the FinBERT model
result = pipeline.analyze_sentiment(file_path=file_path, model=model, enable_cuda=True)

print(f"Sentiment analysis result: {result}")
```

### Features
- Collects news and press releases for specific companies listed on NASDAQ.
- Performs sentiment analysis using the FinBERT model.
-  CUDA acceleration for faster analysis.
