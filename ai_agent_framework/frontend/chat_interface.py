import gradio as gr
from ai_agent_framework.knowledge.knowledge_base import VectorDB
from ai_agent_framework.agents.agent_1001 import Agent1001
# 导入其他 agent 类

class ChatInterface:
    def __init__(self, db_path, openai_api_key):
        self.db_path = db_path
        self.openai_api_key = openai_api_key
        self.agents = {
            "Agent1001": Agent1001,
            # 添加其他 agent
        }

    def chat(self, message, agent_name, history):
        db = VectorDB(self.db_path)
        agent_class = self.agents.get(agent_name)
        if not agent_class:
            return "Invalid agent selected. Please choose a valid agent.", history

        agent = agent_class(db, self.openai_api_key)
        response = agent.answer_question(message)
        
        return response

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

            def user(user_message, history):
                return "", history + [(user_message, None)]

            def bot(history, agent_name):
                user_message = history[-1][0]
                bot_message = self.chat(user_message, agent_name, history[:-1])
                new_history = history[:-1] + [(user_message, bot_message)]
                return new_history

            msg.submit(user, [msg, chatbot], [msg, chatbot], queue=False).then(
                bot, [chatbot, agent_dropdown], chatbot
            )
            clear.click(lambda: None, None, chatbot, queue=False)

        demo.launch()

if __name__ == "__main__":
    # 这里仅用于测试目的，实际使用时应从 main.py 调用
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    db_path = "path/to/your/knowledge.db"
    openai_api_key = os.getenv("OPENAI_API_KEY")
    
    chat_interface = ChatInterface(db_path, openai_api_key)
    chat_interface.launch()
