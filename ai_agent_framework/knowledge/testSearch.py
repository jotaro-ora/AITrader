import os
from knowledge_base import VectorDB
from openai import OpenAI
from dotenv import load_dotenv

# 获取脚本所在目录
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# 构建 .env 文件路径
env_path = os.path.join(os.path.dirname(os.path.dirname(SCRIPT_DIR)), '.env')

# 检查 .env 文件是否存在
if not os.path.exists(env_path):
    raise FileNotFoundError(f".env file not found at {env_path}")

# 加载 .env 文件
load_dotenv(env_path)

# 加载 OpenAI API key
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY not found in .env file")

client = OpenAI(api_key=api_key)

print(f"Successfully loaded API key from {env_path}")

def get_embedding(text):
    """获取文本的嵌入向量"""
    response = client.embeddings.create(
        model="text-embedding-ada-002",
        input=[text]
    )
    return response.data[0].embedding

def main():
    # 构建数据库文件路径
    db_path = os.path.join(SCRIPT_DIR, "knowledge.db")
    
    # 初始化 VectorDB
    db = VectorDB(db_path)
    
    while True:
        # 获取用户输入
        query = input("请输入您的查询（输入 'q' 退出）: ")
        
        if query.lower() == 'q':
            break
        
        # 获取查询的嵌入向量
        query_vector = get_embedding(query)
        
        # 搜索数据库
        results = db.search(query_vector, limit=5)
        
        # 打印结果
        print("\n搜索结果:")
        for result in results:
            print(f"ID: {result['id']}")
            print(f"内容: {result['content'][:100]}...")  # 只打印前100个字符
            print(f"相似度: {result['similarity']}")
            print(f"标签: {result['tags']}")
            print(f"时间戳: {result['timestamp']}")
            print("---")
        
        print("\n")
    
    # 关闭数据库连接
    db.close()

if __name__ == "__main__":
    main()