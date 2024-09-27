import faiss
import numpy as np
import json
import os
from sentence_transformers import SentenceTransformer

class ProductKnowledgeDB:
    def __init__(self, knowledge_file):
        self.model = SentenceTransformer('paraphrase-MiniLM-L6-v2')  # Use a lightweight model
        self.dimension = self.model.get_sentence_embedding_dimension()
        self.index = faiss.IndexFlatL2(self.dimension)
        self.data = []
        self.knowledge_file = knowledge_file
    
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
        embeddings = self.model.encode(texts, show_progress_bar=True)
        self.index.add(np.array(embeddings))
        
        print(f"Loaded {len(self.data)} knowledge entries from {self.knowledge_file}")
    
    def search(self, query, k=5):
        query_embedding = self.model.encode([query])[0]
        distances, indices = self.index.search(np.array([query_embedding]), k)
        return [(self.data[i], distances[0][j]) for j, i in enumerate(indices[0])]
    
    def get_relevant_context(self, query, num_results=5, max_tokens=2000):
        results = self.search(query, k=num_results)
        context = ""
        for text, distance in results:
            if len(context) + len(text) <= max_tokens:
                context += f"{text} (distance: {distance:.4f})\n\n"
            else:
                break
        return context.strip()
