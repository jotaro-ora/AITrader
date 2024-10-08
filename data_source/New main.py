import json
import feedparser
import time
from bs4 import BeautifulSoup


# Class for handling predefined tags and tag extraction logic
class TagExtractor:
    def __init__(self, tag_file='tags.json'):
        # Load tags from the JSON file
        with open(tag_file, 'r') as f:
            data = json.load(f)
            self.predefined_tags = data['tags']

    # Function to extract tags based on content keywords
    def extract_tags(self, content):
        content_lower = content.lower()
        # Extract keywords from predefined tags
        tags = [keyword for keyword in self.predefined_tags if keyword in content_lower]
        return list(set(tags))


# Class to handle fetching RSS feeds and cleaning the content
class RSSFetcher:
    def __init__(self):
        # Dictionary to store RSS URLs by source name
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
            "Chainbuzz": "https://chainbuzz.xyz/rss"  # Added Chainbuzz feed
        }

    # Function to clean HTML content, extract plain text, and decode UTF-8 characters
    @staticmethod
    def clean_html(content):
        if '<html' in content or '<body' in content or '<p' in content:
            # Parse the content with BeautifulSoup if it looks like HTML
            soup = BeautifulSoup(content, 'html.parser')

            # Remove unwanted tags
            for img in soup.find_all('img'):
                img.decompose()
            for tag in soup(['style', 'script']):
                tag.decompose()

            # Get plain text, stripping out any remaining tags
            clean_text = soup.get_text(separator=' ', strip=True)

            # Attempt to decode double-encoded UTF-8, if applicable
            try:
                clean_text = bytes(clean_text, 'utf-8').decode('utf-8')
            except UnicodeDecodeError:
                pass  # Let the text pass through unchanged if there's no issue
            return clean_text
        else:
            return content

    # Function to fetch data from a specific RSS feed
    def fetch_rss_data_with_clean_text(self, rss_url, max_articles):
        feed = feedparser.parse(rss_url)
        new_data = []

        for entry in feed.entries:
            if len(new_data) >= max_articles:
                break

            title = entry.title
            # Get full content or summary if full content is not available
            content = entry.content[0].value if 'content' in entry else entry.get('description', "No content available")

            # Clean HTML to extract only text
            clean_content = self.clean_html(content)

            # Append cleaned content with the title
            new_data.append({
                "data": f"{title} - {clean_content}",
                "source": rss_url,
                "timestamp": int(time.time())  # Add the current timestamp in seconds since epoch
            })

        return new_data

    # Function to fetch articles from all feeds
    def fetch_all_feeds(self, max_articles_per_feed):
        all_articles = []
        for source, url in self.feed_urls.items():
            try:
                articles = self.fetch_rss_data_with_clean_text(url, max_articles_per_feed)
                all_articles.extend(articles)
            except Exception as e:
                print(f"Failed to fetch data from {source}: {e}")
        return all_articles


# Class to manage the knowledge base and update it
class KnowledgeBaseUpdater:
    def __init__(self, database_file='knowledge_base.json'):
        self.database_file = database_file
        self.tag_extractor = TagExtractor()
        self.rss_fetcher = RSSFetcher()

    # Function to load existing articles from the database
    def load_knowledge_base(self):
        try:
            with open(self.database_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return []

    # Function to save articles to the database
    def save_knowledge_base(self, knowledge_base):
        with open(self.database_file, 'w') as f:
            json.dump(knowledge_base[:1000], f, indent=4)  # Save only the first 1000 articles

    # Function to update the knowledge base
    def update_database(self, target_article_count=1000):
        knowledge_base = self.load_knowledge_base()
        current_article_count = len(knowledge_base)

        remaining_articles = target_article_count - current_article_count
        if remaining_articles <= 0:
            print(f"Database already has {current_article_count} or more articles.")
            return

        # Fetch articles from all sources until we reach the target count
        while remaining_articles > 0:
            fetched_articles = self.rss_fetcher.fetch_all_feeds(min(50, remaining_articles))
            for article in fetched_articles:
                # Extract tags from content
                tags = self.tag_extractor.extract_tags(article["data"])
                article["tags"] = tags

                # Add the new article to the knowledge base only if there's still room
                if len(knowledge_base) < target_article_count:
                    knowledge_base.append(article)

            remaining_articles = target_article_count - len(knowledge_base)

        # Save the updated knowledge base
        self.save_knowledge_base(knowledge_base)
        print(f"Database updated successfully with exactly {len(knowledge_base)} articles.")


# Function to trigger database update on one click
def one_click_update():
    updater = KnowledgeBaseUpdater()
    updater.update_database(1000)


if __name__ == "__main__":
    one_click_update()
