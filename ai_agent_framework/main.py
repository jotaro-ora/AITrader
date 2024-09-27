import os
from dotenv import load_dotenv
from agents.problem_analysis import ProblemAnalysisAgent
from agents.product_usage import ProductUsageAgent
from agents.news_history import NewsHistoryAgent
from agents.real_time_analysis import RealTimeAnalysisAgent
from agents.report_aggregation import ReportAggregationAgent
from agents.check import CheckAgent
from database.product_knowledge import ProductKnowledgeDB
from database.news_history import NewsHistoryDB
from database.trading_history import TradingHistoryDB
from frontend.chat_interface import ChatInterface
from api.openai_api import OpenAIAPI

load_dotenv()

class AIAgentFramework:
    def __init__(self):
        
        current_dir = os.path.dirname(os.path.abspath(__file__))
        jojo_product_path = os.path.join(current_dir, 'knowledge', 'JOJOProduct_knowledge.json')
        self.product_db = ProductKnowledgeDB(jojo_product_path)
        self.product_db.load_data()
        self.news_db = NewsHistoryDB()
        self.trading_db = TradingHistoryDB()

        self.openai_api = OpenAIAPI()
        self.problem_analysis = ProblemAnalysisAgent(self.openai_api)
        self.product_usage = ProductUsageAgent(self.openai_api, self.product_db)
        self.news_history = NewsHistoryAgent(self.openai_api)
        self.real_time_analysis = RealTimeAnalysisAgent(self.openai_api)
        self.report_aggregation = ReportAggregationAgent(self.openai_api)
        self.check = CheckAgent(self.openai_api)
        
        self.chat_interface = ChatInterface(self)
    
    def process_query(self, query):
        problem_type = self.problem_analysis.analyze(query)
        
        if "product usage" in problem_type:
            response = self.product_usage.answer(query)
        elif "price prediction" in problem_type:
            news_info = self.news_history.analyze()
            real_time_data = self.real_time_analysis.analyze()
            expert_report = self.report_aggregation.aggregate()
            response = f"News analysis: {news_info}\nReal-time data analysis: {real_time_data}\nExpert report summary: {expert_report}"
        else:
            response = "Sorry, I cannot understand your question type."
        
        # Check the response
        checked_response = self.check.check(response)
        return checked_response

if __name__ == "__main__":
    framework = AIAgentFramework()
    framework.chat_interface.run()