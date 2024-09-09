from .sentiment_analyzer import SentimentAnalyzer
from .datasource import PressReleasesLink, NasdaqNewsLink, YahooFinanceLink, XdFinanseLink, CnbcLink
from .scraper import PressReleasesScrape, NasdaqNewsScrape
from .config import COMPANIES



class DataPipeline:
    def __init__(self, company_name: str, time_frame: str):
        self.company_name = company_name
        self.time_frame = time_frame
        self.links = []
        self.scraper = {
            'press_releases': PressReleasesScrape(),
            'nasdaq_news': NasdaqNewsScrape()
        }
        self.sentiment_analyzer = SentimentAnalyzer()
        self.data_sources = {
            'press_releases': PressReleasesLink(),
            'nasdaq_news': NasdaqNewsLink(),
            'yahoo_finanse': YahooFinanceLink(),
            'xd_finanse': XdFinanseLink(),
            'cnbc': CnbcLink(),
        }

    def collect_links(self, source_name: str):
        data_source = self.data_sources[source_name]
        self.links = data_source.get_links(self.company_name, self.time_frame)
        return self.links

    def scrape_data(self, links: list, source_name: str, folder_path: str):
        scrape_source = self.scraper[source_name]
        scrape_source.extract_info_from_links(self.company_name, links, folder_path)

    def analyze_sentiment(self, articles):
        results = []
        for article in articles:
            sentiment = self.sentiment_analyzer.analyze(article)
            results.append(sentiment)
        return results

    def run_pipeline(self, source_name: str, folder_path: str):
        self.collect_links(source_name)
        self.scrape_data(self.links, source_name, folder_path)
        #sentiment_results = self.analyze_sentiment(articles)
        #return sentiment_results