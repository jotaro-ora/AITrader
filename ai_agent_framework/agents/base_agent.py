from typing import List, Tuple, Optional
from datetime import datetime
from ai_agent_framework.knowledge.knowledge_base import VectorDB

class BaseAgent:
    def __init__(self, knowledge_base: VectorDB):
        self.knowledge_base = knowledge_base
        self.short_term_memory = ""

    def answer_question(self, question: str) -> str:
        """
        Answer the user's question. This is a base method that can be overridden by subclasses to implement different logic.
        
        :param question: The user's question
        :return: The answer
        """
        # Search the knowledge base
        query_vector = self.get_embedding(question)
        search_results = self.search_knowledge_base(query_vector)
        
        # Build context
        context = self._build_context(question, search_results)
        
        # Generate answer (this is a simple implementation, actual applications may need more complex logic or external API calls)
        answer = f"Based on my knowledge, for the question '{question}', my answer is: [Answer content goes here]"
        
        # Update short-term memory
        self._update_short_term_memory(question, answer)
        
        return answer

    def search_knowledge_base(self, query_vector: List[float], limit: int = 5, time_range: Optional[Tuple[datetime, datetime]] = None, tags: Optional[List[str]] = None) -> List[dict]:
        """
        Search the knowledge base with optional time range and tag filters
        
        :param query_vector: The search query vector
        :param limit: The limit on the number of results to return
        :param time_range: Optional tuple of (start_time, end_time) to filter results by timestamp
        :param tags: Optional list of tags to filter results
        :return: A list of search results
        """
        return self.knowledge_base.search(query_vector, limit=limit, time_range=time_range, tags=tags)

    def _build_context(self, question: str, search_results: List[dict]) -> str:
        """
        Build context information
        
        :param question: The user's question
        :param search_results: Knowledge base search results
        :return: The constructed context string
        """
        context = f"Question: {question}\n\nRelevant information:\n"
        for result in search_results:
            content = result['content']
            timestamp = result['timestamp']
            tags = result['tags']
            similarity = result['similarity']
            context += f"- {content} (Timestamp: {timestamp}, Tags: {', '.join(tags)}, Similarity: {similarity:.2f})\n"
        context += f"\nShort-term memory: {self.short_term_memory}"
        return context

    def _update_short_term_memory(self, question: str, answer: str):
        """
        Update short-term memory
        
        :param question: The user's question
        :param answer: The generated answer
        """
        self.short_term_memory = f"Recent question: {question}\nRecent answer: {answer}"

    def get_embedding(self, text: str) -> List[float]:
        """
        Get the embedding for a given text. This method should be implemented by subclasses.
        
        :param text: The text to get the embedding for
        :return: The embedding vector
        """
        raise NotImplementedError("This method should be implemented by subclasses")

