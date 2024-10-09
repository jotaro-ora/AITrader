import os
import sys
import time
from datetime import datetime
from dotenv import load_dotenv

# 添加项目根目录到 Python 路径
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

from ai_agent_framework.agents import Agent1001
from ai_agent_framework.knowledge.knowledge_base import VectorDB

# 加载环境变量
load_dotenv()

# 预定义的问题列表
BENCHMARK_QUESTIONS = [
    "What are your thoughts on BTC right now?",
    "Where are the current support and resistance levels for BTC?",
    "Should I go short or long on BTC, and why?",
    "What do you think about ETH's price at the moment?",
    "Should I go short or long on BTC and ETH? What would be good entry points, stoploss (SL), and takeprofit (TP) levels?",
    "Can you give me a quick technical analysis of BTC and ETH for today?",
    "Are there any fundamental news updates affecting BTC and the overall market right now?",
    "I'm planning to short BTC, How do I determine my position size and the risk management to apply?",
"How do I find the best entry points for BTC and ETH as a day trader?",
    "What is the current market sentiment using the fear and greed index?",
    "Based on the current sentiment, what would be the best decision—whether to enter the market, DCA, take profits, or stay away completely?",
    "What should I do if the price of BTC is at a resistance or support level?",
    "How can I spot a potential BTC reversal using technical indicators or chart patterns?",
    "What are the current funding rates for BTC and ETH?",
    "How can I tell if BTC’s support or resistance levels are strong?",
    "What are the best timeframes for day trading, scalping, and swing trading on BTC?",
    "What’s the best strategy for scalping BTC or ETH in a volatile market?",
    "How do I identify good entry and exit points for swing trading BTC?",
    "How global economic factors like inflation or interest rates affect BTC’s price?",
    "How can I use open interest and volume to gauge market sentiment for BTC and ETH?",
]

def run_benchmark(agent):
    results = []
    total_time = 0

    print(f"Starting benchmark with {agent.__class__.__name__} at {datetime.now()}")
    print("=" * 50)

    for i, question in enumerate(BENCHMARK_QUESTIONS, 1):
        print(f"\nQuestion {i}: {question}")
        start_time = time.time()
        answer = "".join(agent.answer_question(question))  # 使用 answer_question 方法
        end_time = time.time()
        
        duration = end_time - start_time
        total_time += duration
        
        results.append({
            "question": question,
            "answer": answer,
            "time": duration
        })
        
        print(f"Answer: {answer}")
        print(f"Time taken: {duration:.2f} seconds")
        print("-" * 50)

    avg_time = total_time / len(BENCHMARK_QUESTIONS)
    print(f"\nBenchmark complete. Average time per question: {avg_time:.2f} seconds")

    return results

def save_results(results, agent_name):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"benchmark_results_{agent_name}_{timestamp}.txt"
    
    with open(filename, "w") as f:
        f.write(f"Benchmark Results for {agent_name}\n")
        f.write(f"Date: {datetime.now()}\n")
        f.write("=" * 50 + "\n\n")
        
        for i, result in enumerate(results, 1):
            f.write(f"Question {i}: {result['question']}\n")
            f.write(f"Answer: {result['answer']}\n")
            f.write(f"Time taken: {result['time']:.2f} seconds\n")
            f.write("-" * 50 + "\n\n")
        
        avg_time = sum(r['time'] for r in results) / len(results)
        f.write(f"Average time per question: {avg_time:.2f} seconds\n")

    print(f"Results saved to {filename}")

def main():
    # 获取 OpenAI API 密钥
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        raise ValueError("OPENAI_API_KEY not found in environment variables")
    
    # 获取数据库路径
    current_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(current_dir, "..", "knowledge", "knowledge.db")
    
    # 初始化知识库
    knowledge_base = VectorDB(db_path)
    
    # 初始化 Agent1001
    agent = Agent1001(knowledge_base, openai_api_key)
    
    results = run_benchmark(agent)
    save_results(results, agent.__class__.__name__)

if __name__ == "__main__":
    main()