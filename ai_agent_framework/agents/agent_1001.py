import openai
from typing import List, Tuple, Optional, Generator, Deque
from datetime import datetime, timedelta
from collections import deque
from ai_agent_framework.agents.base_agent import BaseAgent
from ai_agent_framework.knowledge.knowledge_base import VectorDB
from openai import OpenAI
from langdetect import detect

def get_language_name(lang_code):
    """
    Convert language code to full name
    """
    lang_map = {
        'zh-cn': 'Chinese (Simplified)',
        'zh-tw': 'Chinese (Traditional)',
        'en': 'English',
        # Add more mappings as needed
    }
    return lang_map.get(lang_code, lang_code)

class Agent1001(BaseAgent):
    def __init__(self, knowledge_base: VectorDB, openai_api_key: str, max_history: int = 5):
        super().__init__(knowledge_base)
        self.client = OpenAI(api_key=openai_api_key)
        self.conversation_history: Deque[Tuple[str, str]] = deque(maxlen=max_history)

    def answer_question(self, question: str, tags: Optional[List[str]] = ["chainbuzz"]) -> Generator[str, None, None]:
        """
        Answer the user's question using GPT-4 and the knowledge base with streaming output.
        Supports multilingual input and output.
        
        :param question: The user's question in any language
        :param tags: Optional list of tags to filter results, defaults to ["chainbuzz"]
        :yield: Chunks of the answer as they are generated in the user's language
        """
        # Detect the language of the question
        source_lang = detect(question)
        language_name = get_language_name(source_lang)

        end_time = datetime.now()
        start_time = end_time - timedelta(days=30)
        
        query_vector = self.get_embedding(question)[0]
        
        search_results = self.knowledge_base.search(
            query_vector, 
            limit=5, 
            time_range=(start_time, end_time), 
            tags=tags
        )
        
        context = self._build_context(question, search_results, language_name)
        
        messages = [
            {"role": "system", "content": f"You are an AI assistant with expertise in trading and cryptocurrency news. Communicate in a warm, conversational tone. Your responses should be concise, engaging, and infused with personality, avoiding unnecessary long-windedness. Use natural, everyday language and avoid technical jargon unless necessary, explaining complex concepts in simple ways. Always consider the previous conversation history and adjust your replies based on the user's prior messages to ensure relevance and coherence. Prioritize understanding the user's underlying needs and intentions, even if they aren't explicitly stated, and offer assistance that addresses these core concerns. If a misunderstanding occurs, politely ask for clarification to keep the conversation flowing smoothly. Where appropriate, include light humor or interesting anecdotes to make interactions more enjoyable without straying from the main topic. IMPORTANT: Always respond in {language_name}."},
            {"role": "user", "content": context}
        ]
        
        # Add conversation history to messages
        for past_question, past_answer in self.conversation_history:
            messages.append({"role": "user", "content": past_question})
            messages.append({"role": "assistant", "content": past_answer})
        
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=messages,
            stream=True
        )
        
        full_answer = ""
        for chunk in response:
            if chunk.choices[0].delta.content is not None:
                content = chunk.choices[0].delta.content
                full_answer += content
                yield content
        
        self._update_conversation_history(question, full_answer)

    def _build_context(self, question: str, search_results: List[dict], language_name: str) -> str:
        """
        Build context information for GPT-4
        
        :param question: The user's question
        :param search_results: Knowledge base search results
        :param language_name: The name of the language to respond in
        :return: The constructed context string
        """
        context = f"Question: {question}\n\nRelevant information from ChainBuzz in the last month:\n"
        for result in search_results:
            content = result['content']
            timestamp = result['timestamp']
            tags = result['tags']
            similarity = result['similarity']
            context += f"- {content} (Timestamp: {timestamp}, Tags: {', '.join(tags)}, Similarity: {similarity:.2f})\n"
        
        if self.conversation_history:
            context += "\nRecent conversation history:\n"
            for past_question, past_answer in self.conversation_history:
                context += f"Q: {past_question}\nA: {past_answer}\n\n"
        
        context += f"Based on the above information from ChainBuzz in the last month and the conversation history, please provide a concise and accurate answer to the question. If the question is similar to a previous one, refer to the previous answer and provide any updates or corrections if necessary. IMPORTANT: Your response must be in {language_name}."
        return context

    def _update_conversation_history(self, question: str, answer: str) -> None:
        """
        Update the conversation history with the latest question and answer.
        
        :param question: The user's question
        :param answer: The AI's answer
        """
        self.conversation_history.append((question, answer))

    def get_embedding(self, text: str) -> List[float]:
        """
        Get the embedding for a given text using OpenAI's API
        
        :param text: The text to get the embedding for
        :return: The embedding vector
        """
        response = self.client.embeddings.create(
            model="text-embedding-ada-002",
            input=[text]
        )
        return [embedding.embedding for embedding in response.data]