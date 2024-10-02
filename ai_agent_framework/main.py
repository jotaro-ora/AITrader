import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv

from ai_agent_framework.agents import agent_registry  # 导入 agent_registry
from ai_agent_framework.knowledge.knowledge_base import VectorDB
from ai_agent_framework.frontend.chat_interface import ChatInterface

# 加载环境变量
load_dotenv()

class AIAgentFramework:
    def __init__(self):
        # 加载环境变量
        load_dotenv()
        
        # 获取 OpenAI API 密钥
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        
        # 获取数据库路径
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.db_path = os.path.join(current_dir, "knowledge", "knowledge.db")
        
        # 初始化知识库
        self.knowledge_base = VectorDB(self.db_path)
        
        # 初始化聊天界面
        self.chat_interface = ChatInterface(self.db_path, self.openai_api_key)

    def process_query(self, query, agent_name):
        # 这里的逻辑保持不变
        pass

if __name__ == "__main__":
    framework = AIAgentFramework()
    framework.chat_interface.launch()