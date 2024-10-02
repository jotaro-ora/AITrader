# AI Agent Framework

这个项目是一个 AI agent 框架，使用 OpenAI 的 GPT 模型来回答有关区块链和加密货币新闻的问题。它包括一个灵活的知识库系统和可定制的基础 agent 设计。

## 项目结构

- `ai_agent_framework/`: 主项目目录
  - `agents/`: 包含不同任务的各种 agent 类
  - `knowledge/`: 包含知识库相关的脚本和类
  - `frontend/`: 使用 Gradio 的聊天界面
  - `main.py`: 应用程序的主入口点

## 前提条件

- Python 3.9 或更高版本
- pip (Python 包管理器)

## 安装

1. 克隆仓库：
   ```
   git clone https://github.com/your-username/ai-agent-framework.git
   cd ai-agent-framework
   ```

2. 创建虚拟环境：
   ```
   python -m venv .venv
   ```

3. 激活虚拟环境：
   - 在 Windows 上：
     ```
     .venv\Scripts\activate
     ```
   - 在 macOS 和 Linux 上：
     ```
     source .venv/bin/activate
     ```

4. 安装所需的包：
   ```
   pip install -r requirements.txt
   ```

5. 设置环境变量：
   在根目录创建一个 `.env` 文件，并添加您的 OpenAI API 密钥：
   ```
   OPENAI_API_KEY=your_api_key_here
   ```

## 运行应用程序

1. 确保您在项目根目录中，并且已激活虚拟环境。

2. 运行主脚本：
   ```
   python ai_agent_framework/main.py
   ```

   这将启动 Gradio 聊天界面。

3. 打开网络浏览器，访问控制台输出中提供的 URL（通常是 `http://127.0.0.1:7860`）。

4. 现在您可以通过聊天界面与 AI agent 进行交互。

## 知识库 (VectorDB)

框架现在包括一个向量数据库 (VectorDB)，用于高效存储和检索知识。

### 特性：

1. 存储文本内容及相关元数据（标签、时间戳）
2. 使用 OpenAI 的 API 将文本转换为向量嵌入
3. 使用向量嵌入进行高效的相似度搜索
4. 通过时间范围和标签过滤搜索结果

### 使用方法：

```python
from ai_agent_framework.knowledge.knowledge_base import VectorDB

# 初始化数据库
db_path = "path/to/your/knowledge.db"
db = VectorDB(db_path)

# 插入数据
db.insert("unique_id", "要存储的内容", ["tag1", "tag2"], "2023-05-01 12:00:00")

# 搜索数据库
results = db.search(query_vector, limit=5, time_range=(start_time, end_time), tags=["tag1"])

# 完成后关闭数据库连接
db.close()
```

## 添加新的 Agent

要创建一个新的 agent，请按照以下步骤操作：

1. 在 `ai_agent_framework/agents/` 目录下创建一个新的 Python 文件，例如 `new_agent.py`。

2. 在新文件中定义您的 agent 类，继承自 `BaseAgent`：

```python
from ai_agent_framework.agents.base_agent import BaseAgent
from ai_agent_framework.knowledge.knowledge_base import VectorDB
from openai import OpenAI

class NewAgent(BaseAgent):
    def __init__(self, knowledge_base: VectorDB, openai_api_key: str):
        super().__init__(knowledge_base)
        self.client = OpenAI(api_key=openai_api_key)

    def answer_question(self, question: str) -> str:
        # 实现您的自定义逻辑
        # 使用 self.knowledge_base 搜索相关信息
        # 使用 OpenAI API 生成回答
        # 返回生成的回答
        pass

    def get_embedding(self, text: str) -> List[float]:
        # 实现获取文本嵌入的方法
        pass
```

3. 在 `ai_agent_framework/agents/__init__.py` 文件中注册您的新 agent：

```python
from .agent_1001 import Agent1001
from .new_agent import NewAgent

agent_registry = {
    "Agent1001": Agent1001,
    "NewAgent": NewAgent,
}
```

4. 更新 `ai_agent_framework/frontend/chat_interface.py` 文件，将新的 agent 添加到可选列表中：

```python
class ChatInterface:
    def __init__(self, db_path, openai_api_key):
        self.db_path = db_path
        self.openai_api_key = openai_api_key
        self.agents = {
            "Agent1001": Agent1001,
            "NewAgent": NewAgent,  # 添加新的 agent
        }
```

## 测试 Agent

要测试新添加的 agent，您可以按照以下步骤操作：

1. 确保您已经运行了 `embeding_chainbuzz.py` 脚本来导入数据到知识库中。

2. 运行主应用程序：
   ```
   python ai_agent_framework/main.py
   ```

3. 在打开的 Gradio 界面中，从下拉菜单选择您的新 agent。

4. 输入一个问题并提交，观察 agent 的回答。

5. 检查控制台输出，查看搜索结果和其他调试信息。

## 自定义

- 要修改知识库，更新 `ai_agent_framework/knowledge/embeding_chainbuzz.py` 文件中的数据导入逻辑。
- 要更改特定 agent 的行为，修改 `agents` 目录中相应的文件。
- 要调整聊天界面，编辑 `frontend/chat_interface.py` 文件。
- 要创建新的自定义 agent，扩展 BaseAgent 类并实现您自己的逻辑。

## 故障排除

- 如果遇到任何包依赖问题，请确保您使用的是正确的 Python 版本，并且已安装 `requirements.txt` 中的所有包。
- 如果遇到 API 错误，请检查 `.env` 文件中的 OpenAI API 密钥是否正确设置。
- 如果知识库为空，请确保已运行 `embeding_chainbuzz.py` 脚本来导入数据。

## 贡献

欢迎贡献！请随时提交 Pull Request。

## 许可证

该项目根据 MIT 许可证授权 - 有关详细信息，请参阅 LICENSE 文件。