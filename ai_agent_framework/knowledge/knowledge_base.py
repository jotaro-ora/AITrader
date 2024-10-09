import os
import sqlite3
from datetime import datetime
import json
import faiss
import numpy as np
import hashlib

class VectorDB:
    TABLE_NAME = 'vectors'

    def __init__(self, db_path):
        self.db_path = db_path
        self.index = None
        self.id_map = {}
        self.vector_dim = 1536  # 假设向量维度为1536，可以根据实际情况调整
        self.initialize_db()
        self.load_vectors()
        print(f"VectorDB initialized. FAISS index size: {self.index.ntotal if self.index else 0}")

    def initialize_db(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(f'''
                CREATE TABLE IF NOT EXISTS {self.TABLE_NAME} (
                    id TEXT PRIMARY KEY,
                    source TEXT,
                    content TEXT,
                    vector BLOB,
                    tags TEXT,
                    timestamp DATETIME
                )
            ''')
            conn.commit()

    def load_vectors(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT COUNT(*) FROM {self.TABLE_NAME}")
            count = cursor.fetchone()[0]
            print(f"Total entries in SQLite database: {count}")

            if count == 0:
                print("No vectors found in the database")
                self.index = faiss.IndexFlatL2(self.vector_dim)
                return

            cursor.execute(f"SELECT id, vector FROM {self.TABLE_NAME}")
            rows = cursor.fetchall()

            vectors = []
            for i, (id, vector_blob) in enumerate(rows):
                try:
                    # 尝试解析 JSON
                    vector_data = json.loads(vector_blob)
                except json.JSONDecodeError:
                    # 如果不是 JSON，假设它已经是一个列表
                    vector_data = vector_blob

                # 确保 vector_data 是一个列表
                if isinstance(vector_data, list):
                    vector = np.array(vector_data, dtype=np.float32)
                else:
                    print(f"Warning: Unexpected vector format for id {id}. Skipping.")
                    continue

                vectors.append(vector)
                self.id_map[i] = id

            if vectors:
                vectors = np.array(vectors).astype('float32')
                self.index = faiss.IndexFlatL2(self.vector_dim)
                self.index.add(vectors)
            else:
                print("No valid vectors found in the database")
                self.index = faiss.IndexFlatL2(self.vector_dim)

    def search(self, query_vector, limit=5, time_range=None, tags=None):
        if self.index is None or self.index.ntotal == 0:
            print("FAISS index is not initialized or empty.")
            return []
        
        query_vector = np.array([query_vector], dtype=np.float32)
        distances, indices = self.index.search(query_vector, self.index.ntotal)  # 搜索所有向量
        
        results = []
        seen_ids = set()  # 用于跟踪已经添加的 ID
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            for i, idx in enumerate(indices[0]):
                id = self.id_map[idx]
                if id in seen_ids:
                    continue  # 跳过已经添加的 ID
                
                cursor.execute(f"SELECT content, timestamp, tags FROM {self.TABLE_NAME} WHERE id = ?", (id,))
                content, timestamp, tags_json = cursor.fetchone()
                
                entry_time = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
                entry_tags = json.loads(tags_json)
                
                if time_range and (entry_time < time_range[0] or entry_time > time_range[1]):
                    continue
                
                if tags and not any(tag in entry_tags for tag in tags):
                    continue
                
                results.append({
                    'id': id,
                    'content': content,
                    'timestamp': timestamp,
                    'tags': entry_tags,
                    'similarity': 1 / (1 + distances[0][i])
                })
                seen_ids.add(id)
                
                if len(results) >= limit:
                    break
        
        results.sort(key=lambda x: x['similarity'], reverse=True)
        return results[:limit]

    def insert(self, source, content, vector, tags, timestamp):
        content_hash = hashlib.md5(content.encode()).hexdigest()
        vector_json = json.dumps(vector)
        tags_json = json.dumps(tags)
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(f'''
            INSERT OR REPLACE INTO {self.TABLE_NAME} (id, source, content, vector, tags, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', (content_hash, source, content, vector_json, tags_json, timestamp))
        
        # 更新 FAISS 索引
        if self.index is None:
            self.index = faiss.IndexFlatL2(self.vector_dim)
        self.index.add(np.array([vector], dtype=np.float32))
        self.id_map[len(self.id_map)] = content_hash
        print(f"Inserted/Updated entry with id: {content_hash}, source: {source}")

    def get_all_ids(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT id FROM {self.TABLE_NAME}")
            return [row[0] for row in cursor.fetchall()]

    def get_all_contents(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT content FROM {self.TABLE_NAME}")
            return [row[0] for row in cursor.fetchall()]

    def close(self):
        # 这个方法保留为了接口一致性，但不需要做任何事情
        pass

    def clear_database(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(f"DELETE FROM {self.TABLE_NAME}")
            conn.commit()
        self.index = faiss.IndexFlatL2(self.vector_dim)
        self.id_map = {}
        print("Database cleared")
