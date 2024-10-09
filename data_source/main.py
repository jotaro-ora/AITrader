import json
import feedparser
import time
from bs4 import BeautifulSoup
import os
from datetime import datetime
import html

# Get the directory of the current script
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Class for handling predefined tags and tag extraction logic
class TagExtractor:
    def __init__(self, tag_file='tags.json'):
        tag_file_path = os.path.join(SCRIPT_DIR, tag_file)
        with open(tag_file_path, 'r') as f:
            data = json.load(f)
            self.predefined_tags = data['tags']

    def extract_tags(self, content):
        content_lower = content.lower()
        tags = [keyword for keyword in self.predefined_tags if keyword in content_lower]
        return list(set(tags))

# Class to handle fetching RSS feeds and cleaning the content
class RSSFetcher:
    def __init__(self):
        self.feed_urls = {
            "Blockworks": "https://blockworks.co/feed/",
            "Cointelegraph": "https://cointelegraph.com/rss",
            "The Block": "https://www.theblock.co/rss", 
            "CryptoSlate": "https://cryptoslate.com/feed/",
            "TodayOnChain": "https://www.todayonchain.com/feed/",
            "CoinDesk": "https://www.coindesk.com/arc/outboundfeeds/rss/",
            "NewsBTC": "https://www.newsbtc.com/feed/",
            "Bitcoin Magazine": "https://bitcoinmagazine.com/.rss/full/",
            "The Defiant": "https://thedefiant.io/feed",
            "BeInCrypto": "https://beincrypto.com/feed/",
            "CryptoBriefing": "https://cryptobriefing.com/feed/",
            "U.Today": "https://u.today/rss",
            "CryptoGlobe": "https://www.cryptoglobe.com/latest/feed/",
            "AMBCrypto": "https://ambcrypto.com/feed/",
            "Cryptopolitan": "https://www.cryptopolitan.com/feed/",
            "Chainbuzz": "https://chainbuzz.xyz/rss"
        }

    @staticmethod
    def clean_html(content):
        if '<html' in content or '<body' in content or '<p' in content:
            soup = BeautifulSoup(content, 'html.parser')
            for img in soup.find_all('img'):
                img.decompose()
            for tag in soup(['style', 'script']):
                tag.decompose()
            clean_text = soup.get_text(separator=' ', strip=True)
            try:
                clean_text = bytes(clean_text, 'utf-8').decode('utf-8')
            except UnicodeDecodeError:
                pass
            return html.unescape(clean_text)
        else:
            return html.unescape(content)

    @staticmethod
    def parse_date(date_string):
        try:
            parsed_date = feedparser._parse_date(date_string)
            if parsed_date:
                return int(time.mktime(parsed_date))
        except:
            pass

        date_formats = [
            "%a, %d %b %Y %H:%M:%S %z",
            "%Y-%m-%dT%H:%M:%S%z",
            "%Y-%m-%d %H:%M:%S",
            "%a, %d %b %Y %H:%M:%S GMT",
            "%Y-%m-%dT%H:%M:%SZ",
        ]

        for format in date_formats:
            try:
                return int(datetime.strptime(date_string, format).timestamp())
            except ValueError:
                continue

        return int(time.time())

    def fetch_rss_data_with_clean_text(self, rss_url):
        feed = feedparser.parse(rss_url)
        new_data = []

        for entry in feed.entries:
            title = entry.title
            content = entry.content[0].value if 'content' in entry else entry.get('description', "No content available")
            
            clean_title = self.clean_html(title)
            clean_content = self.clean_html(content)

            published_date = entry.get('published', entry.get('updated', None))
            if published_date:
                timestamp = self.parse_date(published_date)
            else:
                timestamp = int(time.time())

            new_data.append({
                "data": f"{clean_title} - {clean_content}",
                "source": rss_url,
                "timestamp": timestamp
            })

        return new_data

    def fetch_all_feeds(self):
        all_articles = []
        for source, url in self.feed_urls.items():
            try:
                articles = self.fetch_rss_data_with_clean_text(url)
                all_articles.extend(articles)
                print(f"Fetched {len(articles)} articles from {source}")
            except Exception as e:
                print(f"Failed to fetch data from {source}: {e}")
        return all_articles

# Class to manage the knowledge base and update it
class KnowledgeBaseUpdater:
    def __init__(self, database_file='knowledge_base.json'):
        self.database_file = os.path.join(SCRIPT_DIR, database_file)
        self.tag_extractor = TagExtractor()
        self.rss_fetcher = RSSFetcher()

    def load_knowledge_base(self):
        try:
            with open(self.database_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return []

    def save_knowledge_base(self, knowledge_base):
        with open(self.database_file, 'w', encoding='utf-8') as f:
            json.dump(knowledge_base, f, indent=4, ensure_ascii=False)

    def update_database(self):
        knowledge_base = self.load_knowledge_base()
        fetched_articles = self.rss_fetcher.fetch_all_feeds()
        
        for article in fetched_articles:
            tags = self.tag_extractor.extract_tags(article["data"])
            article["tags"] = tags
            knowledge_base.append(article)

        self.save_knowledge_base(knowledge_base)
        print(f"Database updated successfully with {len(knowledge_base)} articles.")

# Function to trigger database update on one click
def one_click_update():
    updater = KnowledgeBaseUpdater()
    updater.update_database()

if __name__ == "__main__":
    one_click_update()