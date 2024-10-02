import requests
import json
from datetime import datetime, timedelta
import os
import time
from dotenv import load_dotenv

# 加载 .env 文件中的环境变量
load_dotenv()

API_BASE_URL = "https://open-api.chainbuzz.xyz"
API_TOKEN = os.getenv("CHAINBUZZ_API_TOKEN")  # 从 .env 文件中读取 API 令牌

if not API_TOKEN:
    raise ValueError("请在 .env 文件中设置 CHAINBUZZ_API_TOKEN")

# 获取脚本所在的目录
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

def get_news(page=1, page_size=10, date=None):
    url = f"{API_BASE_URL}/theme/list"
    headers = {
        "Authorization": f"Bearer {API_TOKEN}"
    }
    params = {
        "page": page,
        "page_size": page_size,
        "language": "en",
    }
    if date:
        params["date"] = date

    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Request failed: {response.status_code}")
        return None

def save_news(news_data, filename):
    # 使用 os.path.join 来确保文件保存在正确的目录
    file_path = os.path.join(SCRIPT_DIR, filename)
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(news_data, f, ensure_ascii=False, indent=2)

def load_news(filename):
    # 使用 os.path.join 来确保从正确的目录加载文件
    file_path = os.path.join(SCRIPT_DIR, filename)
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def update_news():
    news_file = "chainbuzz_news_en.json"
    all_news = load_news(news_file)

    existing_news_ids = set()
    for date_news in all_news.values():
        for item in date_news:
            existing_news_ids.add(item['article_source_id'])

    current_date = datetime.now().date()
    one_month_ago = current_date - timedelta(days=30)

    new_data_added = False

    while current_date >= one_month_ago:
        date_str = current_date.strftime("%Y-%m-%d")
        page = 1
        date_data_added = False
        while True:
            news_data = get_news(page=page, page_size=50, date=date_str)
            if not news_data or not news_data.get('data', {}).get('list'):
                break

            new_items_added = False
            for item in news_data['data']['list']:
                if item['article_source_id'] not in existing_news_ids:
                    existing_news_ids.add(item['article_source_id'])
                    show_time = datetime.strptime(item['show_time'], "%Y-%m-%dT%H:%M:%SZ")
                    date_key = show_time.strftime("%Y-%m-%d %H:%M")
                    
                    if date_key not in all_news:
                        all_news[date_key] = []
                    
                    all_news[date_key].append(item)
                    new_items_added = True
                    new_data_added = True
                    date_data_added = True

            if not new_items_added or len(news_data['data']['list']) < 50:
                break

            page += 1
            time.sleep(0.2)  # 避免请求过于频繁

        if date_data_added:
            print(f"处理了 {date_str} 的数据")
        else:
            print(f"跳过 {date_str} 的数据，本地已有")

        current_date -= timedelta(days=1)

    if new_data_added:
        save_news(all_news, news_file)
        print(f"新闻更新完成于 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    else:
        print("没有新数据需要更新")

if __name__ == "__main__":
    update_news()
