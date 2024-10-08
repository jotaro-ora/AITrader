import json
import os
from datetime import datetime
from knowledge_base import VectorDB
import numpy as np
from openai import OpenAI
from tqdm import tqdm
from dotenv import load_dotenv

# Get the directory of the script
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Build the path to the .env file (located in the parent directory of ai_agent_framework)
env_path = os.path.join(os.path.dirname(os.path.dirname(SCRIPT_DIR)), '.env')

# Check if the .env file exists
if not os.path.exists(env_path):
    raise FileNotFoundError(f".env file not found at {env_path}")

# Load the .env file
load_dotenv(env_path)

# Load the OpenAI API key
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY not found in .env file")

client = OpenAI(api_key=api_key)

print(f"Successfully loaded API key from {env_path}")

def get_embeddings(texts):
    """Get embeddings for texts in batch using OpenAI API"""
    response = client.embeddings.create(
        model="text-embedding-ada-002",
        input=texts
    )
    return [embedding.embedding for embedding in response.data]

def load_chainbuzz_data(filename):
    """Load chainbuzz data"""
    file_path = os.path.join(os.path.dirname(os.path.dirname(SCRIPT_DIR)), 'data_source', filename)
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def import_to_knowledge_base(db, chainbuzz_data):
    """Import chainbuzz data to knowledge base"""
    existing_ids = set(db.get_all_ids())
    new_items = []
    
    for date, news_list in chainbuzz_data.items():
        for news in news_list:
            if news['article_source_id'] not in existing_ids:
                content = f"Title: {news['title']}\nAbstract: {news['abstract']}"
                timestamp = datetime.strptime(news['show_time'], "%Y-%m-%dT%H:%M:%SZ")
                new_items.append((news['article_source_id'], content, timestamp))

    if not new_items:
        print("No new data to import")
        return

    print(f"Importing {len(new_items)} new items")
    
    # Get embeddings in batch
    contents = [item[1] for item in new_items]
    vectors = get_embeddings(contents)

    # Insert data in batch
    for (article_id, content, timestamp), vector in tqdm(zip(new_items, vectors), total=len(new_items)):
        tags = ["chainbuzz"]
        db.insert(article_id, content, vector, tags, timestamp)
    
    print(f"Successfully imported {len(new_items)} new items")
    print(f"Total items in knowledge base: {len(db.get_all_ids())}")

def main():
    # Get the directory of the script
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Build the path to the database file
    db_path = os.path.join(current_dir, "knowledge.db")
    
    db = VectorDB(db_path)
    
    # Load chainbuzz data
    chainbuzz_data = load_chainbuzz_data("chainbuzz_news_en.json")
    
    # Import data to knowledge base
    import_to_knowledge_base(db, chainbuzz_data)
    
    print("Data import completed")
    
    # Test search functionality
    query = "What is the latest news in blockchain?"
    query_vector = get_embeddings([query])[0]
    results = db.search(query_vector, limit=5)
    
    print("\nSearch results:")
    for result in results:
        print(f"ID: {result['id']}")
        print(f"Content: {result['content'][:100]}...")  # Print only the first 100 characters
        print(f"Similarity: {result['similarity']}")
        print("---")
    
    # Close the database connection
    db.close()

if __name__ == "__main__":
    main()
