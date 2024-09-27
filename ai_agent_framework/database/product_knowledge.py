import faiss
import numpy as np
import json
import os
import hashlib
from openai import OpenAI
from typing import List, Tuple, Union
from pathlib import Path

client = OpenAI()

class ProductKnowledgeDB:
    def __init__(self, knowledge_file, cache_dir='embedding_cache', index_file='faiss_index.bin', data_file='data.json'):
        self.dimension = 1536  # OpenAI's text-embedding-ada-002 dimension
        self.knowledge_file = knowledge_file
        
        # 获取当前文件的绝对路径
        current_file_path = Path(__file__).resolve()
        
        # 构建 ai_agent_framework/knowledge 路径
        knowledge_dir = current_file_path.parent.parent / 'knowledge'
        
        # 确保 knowledge 目录存在
        knowledge_dir.mkdir(parents=True, exist_ok=True)
        
        # 设置所有相关文件和目录的路径
        self.cache_dir = knowledge_dir / cache_dir
        self.index_file = knowledge_dir / index_file
        self.data_file = knowledge_dir / data_file
        
        # 确保 cache_dir 存在
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        self.load_or_create_index()
    
    def load_or_create_index(self):
        if self.index_file.exists() and self.data_file.exists():
            self.index = faiss.read_index(str(self.index_file))
            with self.data_file.open('r', encoding='utf-8') as f:
                self.data = json.load(f)
            print(f"Loaded {len(self.data)} entries from local files")
        else:
            self.index = faiss.IndexFlatL2(self.dimension)
            self.data = []
            self.load_data()
            faiss.write_index(self.index, str(self.index_file))
            with self.data_file.open('w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
            print(f"Created and saved index with {len(self.data)} entries")

    def load_data(self):
        """Load product knowledge data from the specified JSON file"""
        if not os.path.exists(self.knowledge_file):
            raise FileNotFoundError(f"File not found: {self.knowledge_file}")
        
        with open(self.knowledge_file, 'r', encoding='utf-8') as f:
            knowledge_base = json.load(f)
        
        texts = []
        for item in knowledge_base:
            title = item['title']
            for paragraph in item['content']:
                text = f"{title}: {paragraph}"
                texts.append(text)
                self.data.append(text)
        
        # Generate embeddings in batch
        embeddings = self.get_embeddings(texts)
        self.index.add(np.array(embeddings))
        
        print(f"Loaded {len(self.data)} knowledge entries from {self.knowledge_file}")
    
    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        embeddings = []
        batch_size = 100  # Adjust based on OpenAI's rate limits
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i+batch_size]
            batch_embeddings = self.get_batch_embeddings(batch)
            embeddings.extend(batch_embeddings)
        return embeddings
    
    def get_batch_embeddings(self, batch: List[str]) -> List[List[float]]:
        batch_embeddings = []
        for text in batch:
            embedding = self.get_cached_embedding(text)
            if embedding is None:
                response = client.embeddings.create(input=text, model="text-embedding-ada-002")
                embedding = response.data[0].embedding
                self.cache_embedding(text, embedding)
            batch_embeddings.append(embedding)
        return batch_embeddings
    
    def get_cached_embedding(self, text: str) -> Union[List[float], None]:
        cache_file = self.cache_dir / self.get_cache_filename(text)
        if cache_file.exists():
            with cache_file.open('r') as f:
                return json.load(f)
        return None
    
    def cache_embedding(self, text: str, embedding: List[float]):
        cache_file = self.cache_dir / self.get_cache_filename(text)
        with cache_file.open('w') as f:
            json.dump(embedding, f)
    
    def get_cache_filename(self, text: str) -> str:
        return hashlib.md5(text.encode()).hexdigest() + '.json'
    
    def search(self, query: str, k: int = 5) -> List[Tuple[str, float]]:
        query_embedding = self.get_embeddings([query])[0]
        distances, indices = self.index.search(np.array([query_embedding]), k)
        return [(self.data[i], distances[0][j]) for j, i in enumerate(indices[0])]
    
    def get_relevant_context(self, query: str, num_results: int = 5, max_tokens: int = 2000) -> str:
        results = self.search(query, k=num_results)
        context = ""
        for text, distance in results:
            if len(context) + len(text) <= max_tokens:
                context += f"{text} (distance: {distance:.4f})\n\n"
            else:
                break
        return context.strip()
