import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class OpenAIAPI:
    def __init__(self):
        pass

    def chat_completion(self, prompt):
        response = client.chat.completions.create(model="gpt-4",
        messages=[{"role": "user", "content": prompt}])
        return response.choices[0].message.content

    def get_embedding(self, text):
        response = client.embeddings.create(input=text,
        model="text-embedding-ada-002")
        return response.data[0].embedding
