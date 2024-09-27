class NewsHistoryAgent:
    def __init__(self, api):
        self.api = api
    
    def analyze(self):
        prompt = "Please analyze the latest news and summarize relevant historical information."
        response = self.api.chat_completion(prompt)
        return response
