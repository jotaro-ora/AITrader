"""
ChainBuzz API integration module.

This module provides functionality to fetch and update news articles,
X (formerly Twitter) hot topics, and X user feeds from the ChainBuzz API.
"""

import os
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

API_BASE_URL: str = "https://open-api.chainbuzz.xyz"
API_TOKEN: Optional[str] = os.getenv("CHAINBUZZ_API_TOKEN")

if not API_TOKEN:
    raise ValueError("Please set CHAINBUZZ_API_TOKEN in the .env file")

SCRIPT_DIR: str = os.path.dirname(os.path.abspath(__file__))

def make_api_request(endpoint: str, params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Make a request to the ChainBuzz API.

    Args:
        endpoint (str): The API endpoint to request.
        params (Dict[str, Any]): The query parameters for the request.

    Returns:
        Optional[Dict[str, Any]]: The JSON response from the API, or None if the request failed.
    """
    url: str = f"{API_BASE_URL}{endpoint}"
    headers: Dict[str, str] = {"Authorization": f"Bearer {API_TOKEN}"}
    
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"API request failed: {e}")
        return None

def get_news(page: int = 1, page_size: int = 10, date: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """
    Fetch news articles from the ChainBuzz API.

    Args:
        page (int): The page number to fetch.
        page_size (int): The number of items per page.
        date (Optional[str]): The date to fetch news for, in YYYY-MM-DD format.

    Returns:
        Optional[Dict[str, Any]]: The news data, or None if the request failed.
    """
    params: Dict[str, Any] = {
        "page": page,
        "page_size": page_size,
        "language": "en",
    }
    if date:
        params["date"] = date
    return make_api_request("/theme/list", params)

def get_x_hot(tag_id: Optional[int] = None, language: str = "en") -> Optional[Dict[str, Any]]:
    """
    Fetch hot topics from X (formerly Twitter) via the ChainBuzz API.

    Args:
        tag_id (Optional[int]): The tag ID to filter by.
        language (str): The language of the content to fetch.

    Returns:
        Optional[Dict[str, Any]]: The X hot topics data, or None if the request failed.
    """
    params: Dict[str, Any] = {"language": language}
    if tag_id:
        params["tag_id"] = tag_id
    return make_api_request("/twitter/toplist", params)

def get_x_feed(screen_name: str, page: int = 1, page_size: int = 10, start_time: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """
    Fetch X (formerly Twitter) feed for a specific user via the ChainBuzz API.

    Args:
        screen_name (str): The X username to fetch the feed for.
        page (int): The page number to fetch.
        page_size (int): The number of items per page.
        start_time (Optional[str]): The start time for the feed, in YYYY-MM-DD format.

    Returns:
        Optional[Dict[str, Any]]: The X feed data, or None if the request failed.
    """
    params: Dict[str, Any] = {
        "page": page,
        "page_size": page_size,
        "screen_name": screen_name,
    }
    if start_time:
        params["start_time"] = start_time
    return make_api_request("/twitter/feed", params)

def save_data(data: Dict[str, Any], filename: str) -> None:
    """
    Save data to a JSON file.

    Args:
        data (Dict[str, Any]): The data to save.
        filename (str): The name of the file to save the data to.
    """
    file_path: str = os.path.join(SCRIPT_DIR, filename)
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_data(filename: str) -> Dict[str, Any]:
    """
    Load data from a JSON file.

    Args:
        filename (str): The name of the file to load data from.

    Returns:
        Dict[str, Any]: The loaded data, or an empty dictionary if the file doesn't exist.
    """
    file_path: str = os.path.join(SCRIPT_DIR, filename)
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def update_news() -> None:
    """
    Update news articles from the ChainBuzz API and save them to a file.
    """
    news_file: str = "chainbuzz_news_en.json"
    all_news: Dict[str, List[Dict[str, Any]]] = load_data(news_file)
    existing_news_ids: set = set(item['article_source_id'] for date_news in all_news.values() for item in date_news)

    current_date: datetime = datetime.now().date()
    one_month_ago: datetime = current_date - timedelta(days=30)

    new_data_added: bool = False

    while current_date >= one_month_ago:
        date_str: str = current_date.strftime("%Y-%m-%d")
        page: int = 1
        while True:
            news_data: Optional[Dict[str, Any]] = get_news(page=page, page_size=50, date=date_str)
            if not news_data or not news_data.get('data', {}).get('list'):
                break

            for item in news_data['data']['list']:
                if item['article_source_id'] not in existing_news_ids:
                    existing_news_ids.add(item['article_source_id'])
                    show_time: datetime = datetime.strptime(item['show_time'], "%Y-%m-%dT%H:%M:%SZ")
                    date_key: str = show_time.strftime("%Y-%m-%d %H:%M")
                    
                    if date_key not in all_news:
                        all_news[date_key] = []
                    
                    all_news[date_key].append(item)
                    new_data_added = True

            if len(news_data['data']['list']) < 50:
                break

            page += 1
            time.sleep(0.2)  # Avoid too frequent requests

        print(f"Processed data for {date_str}")
        current_date -= timedelta(days=1)

    if new_data_added:
        save_data(all_news, news_file)
        print(f"News update completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    else:
        print("No new data to update")

def update_x_hot() -> None:
    """
    Update X (formerly Twitter) hot topics from the ChainBuzz API and save them to a file.
    """
    x_hot_file: str = "chainbuzz_x_hot.json"
    all_x_hot: Dict[str, List[Dict[str, Any]]] = load_data(x_hot_file)

    x_hot_data: Optional[Dict[str, Any]] = get_x_hot()
    if x_hot_data and x_hot_data.get('data', {}).get('list'):
        current_time: str = datetime.now().strftime("%Y-%m-%d %H:%M")
        all_x_hot[current_time] = x_hot_data['data']['list']
        save_data(all_x_hot, x_hot_file)
        print(f"X HOT data update completed at {current_time}")
    else:
        print("No new X HOT data")

def update_x_feed(screen_name: str, days: int = 7) -> None:
    """
    Update X (formerly Twitter) feed for a specific user from the ChainBuzz API and save it to a file.

    Args:
        screen_name (str): The X username to fetch the feed for.
        days (int): The number of days of historical data to fetch.
    """
    x_feed_file: str = f"chainbuzz_x_feed_{screen_name}.json"
    all_x_feed: Dict[str, Dict[str, Any]] = load_data(x_feed_file)

    start_time: str = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    page: int = 1
    while True:
        x_feed_data: Optional[Dict[str, Any]] = get_x_feed(screen_name, page=page, page_size=50, start_time=start_time)
        if not x_feed_data or not x_feed_data.get('data', {}).get('list'):
            break

        for item in x_feed_data['data']['list']:
            show_time: str = item['show_time']
            if show_time not in all_x_feed:
                all_x_feed[show_time] = item

        if len(x_feed_data['data']['list']) < 50:
            break

        page += 1
        time.sleep(0.2)  # Avoid too frequent requests

    save_data(all_x_feed, x_feed_file)
    print(f"X Feed data update completed for {screen_name}")

if __name__ == "__main__":
    update_news()
    update_x_hot()
    update_x_feed("nake13")  # Example: Update X Feed for a specific user