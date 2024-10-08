import gradio as gr
from ai_agent_framework.knowledge.knowledge_base import VectorDB
from ai_agent_framework.agents.agent_1001 import Agent1001
from typing import Generator, List, Tuple

class ChatInterface:
    def __init__(self, db_path: str, openai_api_key: str):
        self.db_path = db_path
        self.openai_api_key = openai_api_key
        self.agents = {
            "Agent1001": Agent1001,
            # Add other agents
        }

    def chat(self, message: str, agent_name: str, history: List[Tuple[str, str]]) -> Generator[List[Tuple[str, str]], None, None]:
        """
        Process user message and generate a streaming response.

        :param message: User's input message
        :param agent_name: Name of the selected agent
        :param history: Chat history
        :yield: Updated chat history with streaming response
        """
        db = VectorDB(self.db_path)
        agent_class = self.agents.get(agent_name)
        if not agent_class:
            yield history + [(message, "Invalid agent selected. Please choose a valid agent.")]
            return

        agent = agent_class(db, self.openai_api_key)
        response_generator = agent.answer_question(message)
        
        partial_response = ""
        for chunk in response_generator:
            partial_response += chunk
            yield history + [(message, partial_response)]

    def launch(self):
        with gr.Blocks() as demo:
            gr.Markdown("# AI Agent Chat")
            gr.Markdown("Chat with an AI agent about blockchain and cryptocurrency news.")
            
            with gr.Row():
                agent_dropdown = gr.Dropdown(
                    choices=list(self.agents.keys()),
                    label="Select Agent",
                    value="Agent1001"
                )
            
            chatbot = gr.Chatbot()
            msg = gr.Textbox()
            clear = gr.Button("Clear")

            def user(user_message: str, history: List[Tuple[str, str]]) -> Tuple[str, List[Tuple[str, str]]]:
                return "", history + [(user_message, None)]

            def bot(history: List[Tuple[str, str]], agent_name: str) -> Generator[List[Tuple[str, str]], None, None]:
                user_message = history[-1][0]
                for updated_history in self.chat(user_message, agent_name, history[:-1]):
                    yield updated_history

            msg.submit(user, [msg, chatbot], [msg, chatbot], queue=False).then(
                bot, [chatbot, agent_dropdown], chatbot
            )
            clear.click(lambda: None, None, chatbot, queue=False)

        demo.launch()

if __name__ == "__main__":
    # This is for testing purposes only, should be called from main.py in actual use
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    db_path = "path/to/your/knowledge.db"
    openai_api_key = os.getenv("OPENAI_API_KEY")
    
    chat_interface = ChatInterface(db_path, openai_api_key)
    chat_interface.launch()
