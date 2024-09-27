class ProductUsageAgent:
    def __init__(self, api, product_db):
        self.api = api
        self.product_db = product_db
    
    def answer(self, query, num_results=5, max_tokens=2000):
        relevant_context = self.product_db.get_relevant_context(query, num_results=num_results, max_tokens=max_tokens)
        print("Relevant context:", relevant_context)
        
        prompt = f"""Based on the following JOJO product information, please provide a comprehensive answer to the user's question. If the information is insufficient, please indicate which parts cannot be answered:

Relevant information:
{relevant_context}

User question: {query}

Please provide a detailed and accurate answer, citing relevant information when necessary. If the information provided is not sufficient to answer the question, please state so clearly."""
        
        response = self.api.chat_completion(prompt)
        return response
