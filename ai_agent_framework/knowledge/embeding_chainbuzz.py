import json
import os
from datetime import datetime
from knowledge_base import VectorDB
import numpy as np
from openai import OpenAI
from tqdm import tqdm
from dotenv import load_dotenv

# 获取脚本所在的目录
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# 构建 .env 文件的路径（位于 ai_agent_framework 的父目录）
env_path = os.path.join(os.path.dirname(os.path.dirname(SCRIPT_DIR)), '.env')

# 检查 .env 文件是否存在
if not os.path.exists(env_path):
    raise FileNotFoundError(f".env file not found at {env_path}")

# 加载 .env 文件
load_dotenv(env_path)

# 加载 OpenAI API 密钥
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY not found in .env file")

client = OpenAI(api_key=api_key)

print(f"Successfully loaded API key from {env_path}")

def get_embeddings(texts):
    """使用 OpenAI API 批量获取文本的嵌入向量"""
    response = client.embeddings.create(
        model="text-embedding-ada-002",
        input=texts
    )
    return [embedding.embedding for embedding in response.data]

def load_chainbuzz_data(filename):
    """加载 chainbuzz 数据"""
    file_path = os.path.join(SCRIPT_DIR, filename)
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def import_to_knowledge_base(db, chainbuzz_data):
    """将 chainbuzz 数据导入到知识库"""
    existing_ids = set(db.get_all_ids())
    new_items = []
    
    for date, news_list in chainbuzz_data.items():
        for news in news_list:
            if news['article_source_id'] not in existing_ids:
                content = f"Title: {news['title']}\nAbstract: {news['abstract']}"
                timestamp = datetime.strptime(news['show_time'], "%Y-%m-%dT%H:%M:%SZ")
                new_items.append((news['article_source_id'], content, timestamp))

    if not new_items:
        print("没有新数据需要导入")
        return

    print(f"正在导入 {len(new_items)} 条新数据")
    
    # 批量获取嵌入向量
    contents = [item[1] for item in new_items]
    vectors = get_embeddings(contents)

    # 批量插入数据
    for (article_id, content, timestamp), vector in tqdm(zip(new_items, vectors), total=len(new_items)):
        tags = ["chainbuzz"]
        db.insert(article_id, content, vector, tags, timestamp)
    
    print(f"成功导入 {len(new_items)} 条新数据")
    print(f"知识库中总条目数: {len(db.get_all_ids())}")

def main():
    # 获取脚本所在的目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 构建数据库文件的路径
    db_path = os.path.join(current_dir, "knowledge.db")
    
    db = VectorDB(db_path)
    
    # 加载 chainbuzz 数据
    chainbuzz_data = load_chainbuzz_data("chainbuzz_news_en.json")
    
    # 导入数据到知识库
    import_to_knowledge_base(db, chainbuzz_data)
    
    print("数据导入完成")
    
    # 测试搜索功能
    query = "What is the latest news in blockchain?"
    query_vector = get_embeddings([query])[0]
    results = db.search(query_vector, limit=5)
    
    print("\n搜索结果:")
    for result in results:
        print(f"ID: {result['id']}")
        print(f"Content: {result['content'][:100]}...")  # 只打印前100个字符
        print(f"Similarity: {result['similarity']}")
        print("---")
    
    # 关闭数据库连接
    db.close()

if __name__ == "__main__":
    main()
