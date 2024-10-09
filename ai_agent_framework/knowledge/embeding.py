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

def decode_unicode(text):
    """Safely decode Unicode-encoded strings"""
    try:
        # First, try to decode as is
        return text.encode('utf-8').decode('unicode-escape')
    except UnicodeDecodeError:
        # If that fails, try to escape special characters
        escaped = text.replace('"', '\\"')
        try:
            return json.loads(f'"{escaped}"')
        except json.JSONDecodeError:
            # If all else fails, return the original string
            print(f"Warning: Could not decode: {text[:50]}...")  # Print first 50 chars
            return text

def get_embeddings(texts):
    """Get embeddings for texts in batch using OpenAI API"""
    response = client.embeddings.create(
        model="text-embedding-ada-002",
        input=texts
    )
    return [embedding.embedding for embedding in response.data]

def load_knowledge_base_data(filename):
    """Load knowledge base data"""
    file_path = os.path.join(os.path.dirname(os.path.dirname(SCRIPT_DIR)), 'data_source', filename)
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"Loaded {len(data)} items from {filename}")
    
    # Decode Unicode in the loaded data
    for item in data:
        item['data'] = decode_unicode(item['data'])
        item['tags'] = [decode_unicode(tag) for tag in item['tags']]
    
    return data

def import_to_knowledge_base(db, knowledge_base_data):
    """Import all knowledge base data to VectorDB without deduplication"""
    print(f"Total items to import: {len(knowledge_base_data)}")

    # 分批处理，每次处理100个项目
    batch_size = 100
    for i in range(0, len(knowledge_base_data), batch_size):
        batch = knowledge_base_data[i:i+batch_size]
        try:
            contents = [item['data'] for item in batch]
            vectors = get_embeddings(contents)
            for item, vector in zip(batch, vectors):
                try:
                    source = item['source']
                    content = item['data']
                    timestamp = datetime.fromtimestamp(item['timestamp'])
                    tags = item['tags']
                    db.insert(source, content, vector, tags, timestamp)
                except Exception as e:
                    print(f"Error inserting item: {e}")
        except Exception as e:
            print(f"Error getting embeddings for batch {i//batch_size + 1}: {e}")

    print(f"Import completed. Total items in knowledge base: {len(db.get_all_contents())}")

def main():
    # Get the directory of the script
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Build the path to the database file
    db_path = os.path.join(current_dir, "knowledge.db")
    
    # 清空数据库
    db = VectorDB(db_path)
    db.clear_database()
    
    # Load knowledge base data
    knowledge_base_data = load_knowledge_base_data("knowledge_base.json")
    
    print(f"Total items in knowledge_base.json: {len(knowledge_base_data)}")
    
    # Import data to knowledge base
    import_to_knowledge_base(db, knowledge_base_data)
    
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
