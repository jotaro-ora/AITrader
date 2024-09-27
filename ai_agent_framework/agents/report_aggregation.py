class ReportAggregationAgent:
    def __init__(self, api):
        self.api = api
    
    def aggregate(self):
        prompt = "Please collect and summarize analysis reports from human experts, and provide auxiliary advice."
        response = self.api.chat_completion(prompt)
        return response
