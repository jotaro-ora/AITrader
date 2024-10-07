import json
import feedparser
from bs4 import BeautifulSoup



# Class for handling predefined tags and tag extraction logic
class TagExtractor:
    def __init__(self):
        # Load tags from the JSON file
        with open('tags.json', 'r') as f:
            data = json.load(f)
            self.predefined_tags = data['tags']

    # Function to extract tags based on content keywords
    def extract_tags(self, content):
        content_lower = content.lower()

        # Extract keywords from predefined tags
        tags = [keyword for keyword in self.predefined_tags if keyword in content_lower]

        # Remove duplicates and return tags
        return list(set(tags))


# Function to clean HTML content, extract plain text, and decode UTF-8 characters
def clean_html(content):
    # Check if the input resembles HTML
    if '<html' in content or '<body' in content or '<p' in content:
        # Parse the content with BeautifulSoup if it looks like HTML
        soup = BeautifulSoup(content, 'html.parser')

        # Remove all <img> tags entirely
        for img in soup.find_all('img'):
            img.decompose()  # Completely remove the <img> tags from the content

        # Remove all <p> tags with inline styles or that contain unnecessary content
        for p in soup.find_all('p'):
            if p.find('img') or 'style' in p.attrs:
                p.decompose()  # Remove <p> tags with images or inline styles

        # Optionally, remove other unwanted tags like <style>, <script> if needed
        for tag in soup(['style', 'script']):
            tag.decompose()

        # Get plain text, stripping out any remaining tags
        clean_text = soup.get_text(separator=' ', strip=True)

        # Attempt to decode double-encoded UTF-8, if applicable
        try:
            clean_text = bytes(clean_text, 'utf-8').decode('utf-8')
        except UnicodeDecodeError:
            pass  # In case there are no issues with encoding, let the text pass through unchanged

        return clean_text
    else:
        # If it doesn't resemble HTML, return the content as-is
        return content


# Function to fetch data from an RSS feed and clean the content
def fetch_rss_data_with_clean_text(rss_url, max_articles):
    feed = feedparser.parse(rss_url)
    tag_extractor = TagExtractor()  # Initialize the tag extractor class
    new_data = []

    for entry in feed.entries:
        if len(new_data) >= max_articles:
            break

        title = entry.title
        # Try to get full content, otherwise fall back to summary
        if 'content' in entry:
            content = entry.content[0].value  # Full content if available
        elif 'description' in entry:
            content = entry.description  # Description or summary if full content not available
        else:
            content = "No content available"

        # Clean the HTML to extract only text and decode UTF-8
        clean_content = clean_html(content)

        # Extract accurate tags from content using the TagExtractor class
        tags = tag_extractor.extract_tags(clean_content)

        new_data.append({
            "data": f"{title} - {clean_content}",
            "source": rss_url,
            "tags": tags
        })

    return new_data


# Functions to fetch data from multiple RSS feeds with limits on article count
def fetch_data_blockworks(max_articles):
    rss_url = "https://blockworks.co/feed/"
    return fetch_rss_data_with_clean_text(rss_url, max_articles)


def fetch_data_cointelegraph(max_articles):
    rss_url = "https://cointelegraph.com/rss"
    return fetch_rss_data_with_clean_text(rss_url, max_articles)


def fetch_data_the_block(max_articles):
    rss_url = "https://www.theblock.co/rss"
    return fetch_rss_data_with_clean_text(rss_url, max_articles)


def fetch_data_cryptoslate(max_articles):
    rss_url = "https://cryptoslate.com/feed/"
    return fetch_rss_data_with_clean_text(rss_url, max_articles)


def fetch_data_todayonchain(max_articles):
    rss_url = "https://www.todayonchain.com/feed/"
    return fetch_rss_data_with_clean_text(rss_url, max_articles)


def fetch_data_coindesk(max_articles):
    rss_url = "https://www.coindesk.com/arc/outboundfeeds/rss/"
    return fetch_rss_data_with_clean_text(rss_url, max_articles)


def fetch_data_newsbtc(max_articles):
    rss_url = "https://www.newsbtc.com/feed/"
    return fetch_rss_data_with_clean_text(rss_url, max_articles)


def fetch_data_bitcoinmagazine(max_articles):
    rss_url = "https://bitcoinmagazine.com/.rss/full/"
    return fetch_rss_data_with_clean_text(rss_url, max_articles)


def fetch_data_the_defiant(max_articles):
    rss_url = "https://thedefiant.io/feed"
    return fetch_rss_data_with_clean_text(rss_url, max_articles)


def fetch_data_beincrypto(max_articles):
    rss_url = "https://beincrypto.com/feed/"
    return fetch_rss_data_with_clean_text(rss_url, max_articles)


def fetch_data_cryptobriefing(max_articles):
    rss_url = "https://cryptobriefing.com/feed/"
    return fetch_rss_data_with_clean_text(rss_url, max_articles)


def fetch_data_u_today(max_articles):
    rss_url = "https://u.today/rss"
    return fetch_rss_data_with_clean_text(rss_url, max_articles)


def fetch_data_crypto_globe(max_articles):
    rss_url = "https://www.cryptoglobe.com/latest/feed/"
    return fetch_rss_data_with_clean_text(rss_url, max_articles)


def fetch_data_ambcrypto(max_articles):
    rss_url = "https://ambcrypto.com/feed/"
    return fetch_rss_data_with_clean_text(rss_url, max_articles)


def fetch_data_cryptopolitan(max_articles):
    rss_url = "https://www.cryptopolitan.com/feed/"
    return fetch_rss_data_with_clean_text(rss_url, max_articles)


# Function to update the database (knowledge base) with a goal of 1,000 articles
def update_database(target_article_count=1000):
    try:
        with open('knowledge_base.json', 'r') as f:
            knowledge_base = json.load(f)
    except FileNotFoundError:
        knowledge_base = []

    current_article_count = len(knowledge_base)

    # We will fetch articles until we have reached the target count (1,000)
    remaining_articles = target_article_count - current_article_count
    if remaining_articles <= 0:
        print(f"Database already has {current_article_count} or more articles.")
        return

    # List of functions to fetch from multiple sources
    fetch_functions = [
        fetch_data_blockworks,
        fetch_data_cointelegraph,
        fetch_data_the_block,
        fetch_data_cryptoslate,
        fetch_data_todayonchain,
        fetch_data_coindesk,
        fetch_data_newsbtc,
        fetch_data_bitcoinmagazine,
        fetch_data_the_defiant,
        fetch_data_beincrypto,
        fetch_data_cryptobriefing,
        fetch_data_u_today,
        fetch_data_crypto_globe,
        fetch_data_ambcrypto,
        fetch_data_cryptopolitan
    ]

    # Iterating through all feeds to collect articles
    while remaining_articles > 0:
        for fetch_func in fetch_functions:
            if remaining_articles <= 0:
                break  # Stop if we have already reached 1,000 articles

            # Fetch 100 articles at a time to prevent fetching too many in one go
            fetched_articles = fetch_func(min(100, remaining_articles))
            knowledge_base.extend(fetched_articles)
            remaining_articles = target_article_count - len(knowledge_base)

    # Save updated knowledge base back to the database (JSON file)
    with open('knowledge_base.json', 'w') as f:
        json.dump(knowledge_base, f, indent=4)

    print(f"Database updated successfully with {len(knowledge_base)} articles.")


# Function to trigger database update on one click
def one_click_update():
    update_database(1000)  # Populate up to 1,000 articles


if __name__ == "__main__":
    one_click_update()
