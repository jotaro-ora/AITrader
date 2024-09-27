import requests
from bs4 import BeautifulSoup
import json
import time
from urllib.parse import urljoin

def fetch_page_content(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.text

def parse_page(html_content, url):
    soup = BeautifulSoup(html_content, 'html.parser')
    
    title = soup.find('h1').text.strip() if soup.find('h1') else "Untitled"
    
    print(f"URL: {url}")
    print(f"Title: {title}")
    
    # 尝试查找主要内容
    content_div = soup.find('div', class_='page-wrapper')
    if content_div:
        content_div = content_div.find('div', class_='page-inner')
    
    if not content_div:
        content_div = soup.find('main')
    
    if content_div:
        print(f"Found content div: {content_div.name}, class: {content_div.get('class')}")
        
        # Extract all text content, including headers
        content = []
        for element in content_div.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'ul', 'ol', 'li', 'pre', 'code']):
            if element.name.startswith('h'):
                content.append(f"{'#' * int(element.name[1:])} {element.get_text(strip=True)}")
            elif element.name in ['ul', 'ol']:
                for li in element.find_all('li', recursive=False):
                    content.append(f"- {li.get_text(strip=True)}")
            elif element.name in ['pre', 'code']:
                content.append(f"```\n{element.get_text(strip=True)}\n```")
            else:
                content.append(element.get_text(strip=True))
        
        # Remove duplicates
        paragraphs = list(dict.fromkeys([p for p in content if p.strip()]))
    else:
        print("Content div not found")
        paragraphs = []

    print(f"Paragraphs: {len(paragraphs)}")
    
    if not paragraphs:
        print("No paragraphs found, trying to extract all text")
        all_text = soup.get_text(strip=True)
        paragraphs = [all_text]

    return {
        "url": url,
        "title": title,
        "content": paragraphs
    }

def crawl_gitbook(base_url):
    knowledge_base = []
    visited_urls = set()
    to_visit = [base_url]
    
    while to_visit:
        url = to_visit.pop(0)
        if url in visited_urls:
            continue
        
        print(f"\nCrawling: {url}")
        try:
            html_content = fetch_page_content(url)
            page_data = parse_page(html_content, url)
            if page_data['content']:
                knowledge_base.append(page_data)
            visited_urls.add(url)
            
            soup = BeautifulSoup(html_content, 'html.parser')
            for link in soup.find_all('a', href=True):
                next_url = urljoin(base_url, link['href'])
                if next_url.startswith(base_url) and next_url not in visited_urls:
                    to_visit.append(next_url)
        except Exception as e:
            print(f"Error crawling {url}: {str(e)}")
        
        time.sleep(0.5)  # Reduced wait time to 0.5 seconds
    
    return knowledge_base

def save_to_json(knowledge_base, output_file):
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(knowledge_base, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    base_url = "https://about.jojo.exchange/"
    output_file = "JOJOProduct_knowledge.json"
    
    knowledge_base = crawl_gitbook(base_url)
    save_to_json(knowledge_base, output_file)
    print(f"\nKnowledge base saved to {output_file}")
    print(f"Total crawled pages: {len(knowledge_base)}")
