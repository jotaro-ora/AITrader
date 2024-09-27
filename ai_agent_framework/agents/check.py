class CheckAgent:
    def __init__(self, api):
        self.api = api
    
    def check(self, text):
        prompt = f"Please check the following text for common sense errors, grammatical errors, factual errors, repetitive or ambiguous statements. If any are found, please correct them:\n\n{text}"
        response = self.api.chat_completion(prompt)
        return response
