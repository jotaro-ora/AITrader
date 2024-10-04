import openai
from typing import List, Tuple, Optional, Generator
from datetime import datetime, timedelta
from ai_agent_framework.agents.base_agent import BaseAgent
from ai_agent_framework.knowledge.knowledge_base import VectorDB
from openai import OpenAI

class Agent1001(BaseAgent):
    def __init__(self, knowledge_base: VectorDB, openai_api_key: str):
        super().__init__(knowledge_base)
        self.client = OpenAI(api_key=openai_api_key)

    def answer_question(self, question: str, tags: Optional[List[str]] = ["chainbuzz"]) -> Generator[str, None, None]:
        """
        Answer the user's question using GPT-4 and the knowledge base with streaming output.
        
        :param question: The user's question
        :param tags: Optional list of tags to filter results, defaults to ["chainbuzz"]
        :yield: Chunks of the answer as they are generated
        """
        # Set time range to last month
        end_time = datetime.now()
        start_time = end_time - timedelta(days=30)
        
        # 获取问题的嵌入向量
        query_vector = self.get_embedding(question)[0]
        print(f"Query vector shape: {len(query_vector)}")
        
        # 使用更新后的 search 法
        search_results = self.knowledge_base.search(
            query_vector, 
            limit=5, 
            time_range=(start_time, end_time), 
            tags=tags
        )
        print(f"Searching with tags: {tags}")
        print(f"Time range: from {start_time} to {end_time}")
        print(f"Number of search results: {len(search_results)}")
        print("\nRelevant news summaries:")
        for result in search_results:
            print(f"Result id: {result['id']}")
            print(f"Content: {result['content'][:200]}...")  # 打印前200个字符作为摘要
            print(f"Tags: {result['tags']}")
            print(f"Timestamp: {result['timestamp']}")
            print(f"Similarity: {result['similarity']:.4f}")
            print("---")
        
        context = self._build_context(question, search_results)
        
        # Use OpenAI API to generate an answer with GPT-4 in streaming mode
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an AI assistant with expertise in blockchain and cryptocurrency news, especially from ChainBuzz. Please answer the question based on the provided context, focusing on information from the last month."},
                {"role": "user", "content": context}
            ],
            stream=True  # Enable streaming
        )
        
        full_answer = ""
        for chunk in response:
            if chunk.choices[0].delta.content is not None:
                content = chunk.choices[0].delta.content
                full_answer += content
                yield content
        
        self._update_short_term_memory(question, full_answer)

    def _build_context(self, question: str, search_results: List[dict]) -> str:
        """
        Build context information for GPT-4
        
        :param question: The user's question
        :param search_results: Knowledge base search results
        :return: The constructed context string
        """
        context = f"Question: {question}\n\nRelevant information from ChainBuzz in the last month:\n"
        for result in search_results:
            content = result['content']
            timestamp = result['timestamp']
            tags = result['tags']
            similarity = result['similarity']
            context += f"- {content} (Timestamp: {timestamp}, Tags: {', '.join(tags)}, Similarity: {similarity:.2f})\n"
        context += f"\nShort-term memory: {self.short_term_memory}\n\n"
        context += "Based on the above information from ChainBuzz in the last month, please provide a concise and accurate answer to the question."
        return context

    def get_embedding(self, text: str) -> List[float]:
        """
        Get the embedding for a given text using OpenAI's API
        
        :param text: The text to get the embedding for
        :return: The embedding vector
        """
        response = self.client.embeddings.create(
            model="text-embedding-ada-002",
            input=[text]  # 注意这里的变化，我们现在传入一个列表
        )
        return [embedding.embedding for embedding in response.data]  # 返回一个列表的嵌入向量