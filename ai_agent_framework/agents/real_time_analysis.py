class RealTimeAnalysisAgent:
    def __init__(self, api):
        self.api = api
    
    def analyze(self):
        prompt = "Please analyze real-time data and generate a technical analysis report."
        response = self.api.chat_completion(prompt)
        return response
