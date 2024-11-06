import os
import pandas as pd
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

from .sentiment_analyzer import SentimentAnalyzer
from .data_source import PressReleasesLink, NasdaqNewsLink
from .scraper import PressReleasesScrape, NasdaqNewsScrape


class DataPipeline:
    def __init__(self):
        """
        Initializes the DataPipeline object.
        """
        self.links = []
        self.scraper = {
            'press_releases': PressReleasesScrape(),
            'nasdaq_news': NasdaqNewsScrape()
        }
        self.sentiment_analyzer = SentimentAnalyzer()
        self.data_sources = {
            'press_releases': PressReleasesLink(),
            'nasdaq_news': NasdaqNewsLink()
        }

    @staticmethod
    def _process_time_frame(time_frame: str):
        """
        Converts the time_frame string into a datetime object.

        :param time_frame: A string representing the time frame.
        :return: A datetime object representing the starting point for data collection.
        """
        today = datetime.now()

        if time_frame == "1 day ago":
            return today - timedelta(days=1)
        elif time_frame == "1 week ago":
            return today - timedelta(weeks=1)
        elif time_frame == "1 month ago":
            return today - relativedelta(months=1)
        else:
            try:
                # Assuming the date is provided in YYYY-MM-DD format
                input_date = datetime.strptime(time_frame, "%Y-%m-%d")
                if input_date > today:
                    raise ValueError("The provided date cannot be in the future.")
                return input_date
            except ValueError as e:
                raise ValueError(f"Invalid date format or {str(e)}")

    @staticmethod
    def download_news(folder_name: str) -> pd.DataFrame:
        """
        Loads all CSV files from the specified folder and combines them into a single DataFrame.

        :param folder_name: The folder containing the CSV files.
        :return: A combined DataFrame with all news data.
        """
        dataframes = []
        for filename in os.listdir(folder_name):
            if filename.endswith('.csv'):
                file_path = os.path.join(folder_name, filename)
                df = pd.read_csv(file_path, encoding='utf-8')
                df['source_file'] = os.path.splitext(filename)[0]
                dataframes.append(df)

        combined_df = pd.concat(dataframes, ignore_index=True)
        return combined_df

    def collect_links(self, company_name: str, time_frame: str, source_name: str, chrome_driver_path: str):
        """
        Collects links from the specified data source.

        :param company_name: The name of the company to collect data for. Allowed names are:
                                'AMD', 'TSLA', 'AMZN', 'AAPL', 'NFLX', 'NVDA', 'MSFT', 'JD', 'CSCO', 'META'.
        :param time_frame: The time frame for data collection. Allowed formats are:
                                "YYYY-MM-DD", "1 day ago", "1 week ago", or "1 month ago".
        :param chrome_driver_path: The path to the ChromeDriver executable.
        :param source_name: The name of the data source. Allowed names are: 'press_releases' or 'nasdaq_news'.
        :return: A list of collected links.
        """
        time_frame = self._process_time_frame(time_frame)
        data_source = self.data_sources[source_name]
        if not data_source:
            raise ValueError(
                f"Invalid data source '{source_name}'. Allowed values are 'press_releases' or 'nasdaq_news'.")

        self.links = data_source.get_links(company_name, time_frame, chrome_driver_path)
        return self.links

    def scrape_data(self, links: list, company_name: str, source_name: str, folder_path: str):
        """
        Scrapes data from the provided links and stores them in the specified folder.

        :param company_name: The name of the company to collect data for. Allowed names are:
                                'AMD', 'TSLA', 'AMZN', 'AAPL', 'NFLX', 'NVDA', 'MSFT', 'JD', 'CSCO', 'META'.
        :param links: A list of URLs to scrape data from.
        :param source_name: The name of the data source. Allowed names are: 'press_releases' or 'nasdaq_news'.
        :param folder_path: The folder path to store scraped data.
        :return: The path to the scraped data file.
        """
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
            print(f"Folder '{folder_path}' did not exist and was created.")

        scraper = self.scraper[source_name]
        if not scraper:
            raise ValueError(
                f"Invalid source name '{source_name}'. Allowed values are 'press_releases' or 'nasdaq_news'.")

        file_path = scraper.extract_info_from_links(company_name, links, folder_path)
        return file_path

    def analyze_sentiment(self, df: pd.DataFrame = None, folder_extract_path: str = None, file_path: str = None,
                          enable_cuda: bool = False, model: int = None, batch_size: int = None) -> float:
        """
        Analyzes sentiment from a DataFrame or CSV files in a folder.

        :param df: The DataFrame containing the data for sentiment analysis
                (if folder_extract_path and file_path are not provided).
        :param folder_extract_path: The folder containing CSV files (if dj and file_path are not provided).
        :param file_path: The path to a CSV file (if folder_extract_path and dj are not provided).
        :param enable_cuda: Boolean to enable CUDA for faster processing.
        :param model: Specifies which model to use (0, 1, or None for the default model).
        :param batch_size: The batch size for processing text data. Uses default if not specified.
        :return: The overall sentiment score.
        """
        if sum(option is not None for option in [df, folder_extract_path, file_path]) != 1:
            raise ValueError("Exactly one of 'df', 'folder_extract_path', or 'file_path' must be provided.")

        if folder_extract_path:
            try:
                df = self.download_news(folder_extract_path)
            except Exception as e:
                raise ValueError(f"Failed to load data from folder '{folder_extract_path}': {e}")
        elif file_path:
            try:
                df = pd.read_csv(file_path, encoding='utf-8')
            except Exception as e:
                raise ValueError(f"Failed to read CSV file from '{file_path}': {e}")

        if 'Content' not in df.columns:
            raise ValueError("The DataFrame must contain a 'Content' column for sentiment analysis.")

        sentiment_score = self.sentiment_analyzer.analyze(data=df, enable_cuda=enable_cuda, model_choice=model,
                                                          batch_size=batch_size)

        sentiment_label = (
            "Positive" if sentiment_score > 0.33 else
            "Negative" if sentiment_score < -0.33 else
            "Neutral"
        )
        print(f"{sentiment_label} Sentiment ({sentiment_score:.2f})")

        return sentiment_score

    def run_pipeline(self, company_name: str, time_frame: str, source_name: str, chrome_driver_path: str,
                     folder_path: str, enable_cuda: bool = False, model: int = None, batch_size: int = None) -> float:
        """
        Runs the complete data pipeline: collects links, scrapes data, and analyzes sentiment.

        :param company_name: The name of the company to collect data for. Allowed names are:
                                'AMD', 'TSLA', 'AMZN', 'AAPL', 'NFLX', 'NVDA', 'MSFT', 'JD', 'CSCO', 'META'.
        :param time_frame: The time frame for data collection. Allowed formats are:
                                "YYYY-MM-DD", "1 day ago", "1 week ago", or "1 month ago".
        :param chrome_driver_path: The path to the ChromeDriver executable.
        :param source_name: The name of the data source. Allowed names are: 'press_releases' or 'nasdaq_news'.
        :param folder_path: The folder path to store scraped data.
        :param enable_cuda: Boolean to enable CUDA for faster processing.
        :param model: Specifies which model to use (0, 1, or None for the default model).
        :param batch_size: The batch size for processing text data. Uses default if not specified.
        :return: The overall sentiment score.
        """
        self.collect_links(company_name=company_name, time_frame=time_frame, source_name=source_name,
                           chrome_driver_path=chrome_driver_path)
        file_path = self.scrape_data(links=self.links, company_name=company_name, source_name=source_name,
                                     folder_path=folder_path)
        sentiment_score = self.analyze_sentiment(file_path=file_path, enable_cuda=enable_cuda, model=model,
                                                 batch_size=batch_size)
        return sentiment_score
