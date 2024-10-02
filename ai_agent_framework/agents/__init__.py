from typing import Dict, Type
from .base_agent import BaseAgent
from .agent_1001 import Agent1001

agent_registry: Dict[str, Type[BaseAgent]] = {
    "Agent1001": Agent1001,
    # 其他 agent 可以在这里注册
}

def get_agent(agent_name: str) -> Type[BaseAgent]:
    return agent_registry.get(agent_name)