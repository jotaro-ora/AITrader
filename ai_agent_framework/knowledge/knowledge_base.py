import os
import sqlite3
from datetime import datetime
import json
import faiss
import numpy as np

class VectorDB:
    def __init__(self, db_path):
        self.db_path = db_path
        self.index = None
        self.id_map = {}
        self.initialize_db()
        self.load_vectors()
        print(f"VectorDB initialized. FAISS index size: {self.index.ntotal if self.index else 0}")

    def initialize_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
            CREATE TABLE IF NOT EXISTS knowledge (
                id TEXT PRIMARY KEY,
                content TEXT NOT NULL,
                vector TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                tags TEXT
            )
            ''')

    def load_vectors(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM knowledge")
            total_count = cursor.fetchone()[0]
            print(f"Total entries in SQLite database: {total_count}")

            cursor.execute("SELECT id, vector FROM knowledge")
            vectors = []
            for idx, (id, vector_json) in enumerate(cursor):
                try:
                    vector = np.array(json.loads(vector_json), dtype=np.float32)
                    vectors.append(vector)
                    self.id_map[idx] = id
                except json.JSONDecodeError:
                    print(f"Error decoding vector for id {id}")
                except Exception as e:
                    print(f"Error processing vector for id {id}: {str(e)}")

        if vectors:
            vectors = np.array(vectors)
            self.index = faiss.IndexFlatL2(vectors.shape[1])
            self.index.add(vectors)
            print(f"Loaded {len(vectors)} vectors into FAISS index")
        else:
            print("No vectors found in the database")

    def search(self, query_vector, limit=5, time_range=None, tags=None):
        if self.index is None or self.index.ntotal == 0:
            print("FAISS index is not initialized or empty.")
            return []
        
        query_vector = np.array([query_vector], dtype=np.float32)
        distances, indices = self.index.search(query_vector, self.index.ntotal)
        
        print(f"Total vectors in FAISS index: {self.index.ntotal}")
        print(f"Number of results from FAISS search: {len(indices[0])}")
        
        results = []
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            for i, idx in enumerate(indices[0]):
                id = self.id_map[idx]
                cursor.execute("SELECT content, timestamp, tags FROM knowledge WHERE id = ?", (id,))
                content, timestamp, tags_json = cursor.fetchone()
                
                entry_time = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
                entry_tags = json.loads(tags_json)
                
                if time_range and (entry_time < time_range[0] or entry_time > time_range[1]):
                    print(f"Skipping entry {id} due to time range filter")
                    continue
                
                if tags and not any(tag in entry_tags for tag in tags):
                    print(f"Skipping entry {id} due to tag filter")
                    continue
                
                results.append({
                    'id': id,
                    'content': content,
                    'timestamp': timestamp,
                    'tags': entry_tags,
                    'similarity': 1 / (1 + distances[0][i])
                })
                
                if len(results) >= limit:
                    break
        
        print(f"Number of results after filtering: {len(results)}")
        return results

    def insert(self, id, content, vector, tags, timestamp):
        vector_json = json.dumps(vector)
        tags_json = json.dumps(tags)
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
            INSERT OR REPLACE INTO knowledge (id, content, vector, tags, timestamp)
            VALUES (?, ?, ?, ?, ?)
            ''', (id, content, vector_json, tags_json, timestamp))
        
        # 更新 FAISS 索引
        if self.index is None:
            self.index = faiss.IndexFlatL2(len(vector))
        self.index.add(np.array([vector], dtype=np.float32))
        self.id_map[len(self.id_map)] = id
        print(f"Inserted/Updated entry with id: {id}, tags: {tags}")

    def get_all_ids(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM knowledge")
            return [row[0] for row in cursor.fetchall()]

    def close(self):
        self.conn.close()
