class ProblemAnalysisAgent:
    def __init__(self, api):
        self.api = api
    
    def analyze(self, query):
        prompt = f"Please analyze the following question and categorize it as either a product usage question or a price prediction question. If the question overlaps, please split it into two separate questions:\n\n{query}"
        response = self.api.chat_completion(prompt)
        return response
