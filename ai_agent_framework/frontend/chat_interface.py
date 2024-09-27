import gradio as gr

class ChatInterface:
    def __init__(self, framework):
        self.framework = framework
    
    def chat(self, message, history):
        response = self.framework.process_query(message)
        return response
    
    def run(self):
        interface = gr.ChatInterface(
            fn=self.chat,
            title="AI Agent Framework Chat",
            description="Chat with the AI Agent Framework"
        )
        interface.launch()
