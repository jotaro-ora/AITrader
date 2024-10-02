# AI Agent Framework

This project is an AI agent framework that uses OpenAI's GPT models to answer questions about blockchain and cryptocurrency news. It includes a flexible knowledge base system and a customizable base agent design.

## Project Structure

- `ai_agent_framework/`: Main project directory
  - `agents/`: Contains various agent classes for different tasks
  - `knowledge/`: Contains scripts and classes related to the knowledge base
  - `frontend/`: Chat interface using Gradio
  - `main.py`: Main entry point of the application

## Prerequisites

- Python 3.9 or higher
- pip (Python package manager)

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/your-username/ai-agent-framework.git
   cd ai-agent-framework
   ```

2. Create a virtual environment:
   ```
   python -m venv .venv
   ```

3. Activate the virtual environment:
   - On Windows:
     ```
     .venv\Scripts\activate
     ```
   - On macOS and Linux:
     ```
     source .venv/bin/activate
     ```

4. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

5. Set up environment variables:
   Create a `.env` file in the root directory and add your OpenAI API key:
   ```
   OPENAI_API_KEY=your_api_key_here
   ```

## Running the Application

1. Ensure you're in the project root directory and your virtual environment is activated.

2. Run the main script:
   ```
   python ai_agent_framework/main.py
   ```

   This will start the Gradio chat interface.

3. Open your web browser and go to the URL provided in the console output (usually `http://127.0.0.1:7860`).

4. You can now interact with the AI agent through the chat interface.

## Knowledge Base (VectorDB)

The framework includes a Vector Database (VectorDB) for efficient storage and retrieval of knowledge.

### Features:

1. Store text content with associated metadata (tags, timestamp)
2. Convert text to vector embeddings using OpenAI's API
3. Efficient similarity search using vector embeddings
4. Filter search results by time range and tags

### Usage:

```python
from ai_agent_framework.knowledge.knowledge_base import VectorDB

# Initialize the database
db_path = "path/to/your/knowledge.db"
db = VectorDB(db_path)

# Insert data
db.insert("unique_id", "Content to be stored", ["tag1", "tag2"], "2023-05-01 12:00:00")

# Search the database
results = db.search(query_vector, limit=5, time_range=(start_time, end_time), tags=["tag1"])

# Close the database connection when done
db.close()
```

## Adding a New Agent

To create a new agent, follow these steps:

1. Create a new Python file in the `ai_agent_framework/agents/` directory, e.g., `new_agent.py`.

2. Define your agent class in the new file, inheriting from `BaseAgent`:

```python
from ai_agent_framework.agents.base_agent import BaseAgent
from ai_agent_framework.knowledge.knowledge_base import VectorDB
from openai import OpenAI

class NewAgent(BaseAgent):
    def __init__(self, knowledge_base: VectorDB, openai_api_key: str):
        super().__init__(knowledge_base)
        self.client = OpenAI(api_key=openai_api_key)

    def answer_question(self, question: str) -> str:
        # Implement your custom logic
        # Use self.knowledge_base to search for relevant information
        # Use OpenAI API to generate an answer
        # Return the generated answer
        pass

    def get_embedding(self, text: str) -> List[float]:
        # Implement method to get text embeddings
        pass
```

3. Register your new agent in the `ai_agent_framework/agents/__init__.py` file:

```python
from .agent_1001 import Agent1001
from .new_agent import NewAgent

agent_registry = {
    "Agent1001": Agent1001,
    "NewAgent": NewAgent,
}
```

4. Update the `ai_agent_framework/frontend/chat_interface.py` file to add the new agent to the selection list:

```python
class ChatInterface:
    def __init__(self, db_path, openai_api_key):
        self.db_path = db_path
        self.openai_api_key = openai_api_key
        self.agents = {
            "Agent1001": Agent1001,
            "NewAgent": NewAgent,  # Add the new agent
        }
```

## Testing an Agent

To test a newly added agent, follow these steps:

1. Ensure you have run the `embeding_chainbuzz.py` script to import data into the knowledge base.

2. Run the main application:
   ```
   python ai_agent_framework/main.py
   ```

3. In the opened Gradio interface, select your new agent from the dropdown menu.

4. Enter a question and submit it, observe the agent's response.

5. Check the console output for search results and other debugging information.

## Customization

- To modify the knowledge base, update the data import logic in the `ai_agent_framework/knowledge/embeding_chainbuzz.py` file.
- To change the behavior of specific agents, modify the corresponding files in the `agents` directory.
- To adjust the chat interface, edit the `frontend/chat_interface.py` file.
- To create new custom agents, extend the BaseAgent class and implement your own logic.

## Troubleshooting

- If you encounter any issues with package dependencies, make sure you're using the correct Python version and that all packages in `requirements.txt` are installed.
- If you get an API error, check that your OpenAI API key is correctly set in the `.env` file.
- If the knowledge base is empty, make sure you've run the `embeding_chainbuzz.py` script to import data.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.