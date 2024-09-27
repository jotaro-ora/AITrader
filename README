# AI Agent Framework

This project is an AI agent framework that uses OpenAI's GPT models to answer questions about JOJO products and perform various analyses.

## Project Structure

- `ai_agent_framework/`: Main project directory
  - `agents/`: Contains various agent classes for different tasks
  - `api/`: API integration (currently OpenAI)
  - `database/`: Database classes for product knowledge, news, and trading history
  - `frontend/`: Chat interface using Gradio
  - `knowledge/`: Contains scripts for crawling and processing product knowledge
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

## Customization

- To modify the product knowledge base, update the `JOJOProduct_knowledge.json` file in the `knowledge` directory.
- To change the behavior of specific agents, modify the corresponding files in the `agents` directory.
- To adjust the chat interface, edit the `chat_interface.py` file in the `frontend` directory.

## Troubleshooting

- If you encounter any issues with package dependencies, make sure you're using the correct Python version and that all packages in `requirements.txt` are installed.
- If you get an API error, check that your OpenAI API key is correctly set in the `.env` file.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
