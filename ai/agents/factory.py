# ai/agents/factory.py
from ai.agents.definitions import ROLES

class AgentFactory:
    @staticmethod
    def build_agent(role_key):
        if role_key not in ROLES:
            raise ValueError(f"El rol {role_key} no está definido.")
        return ROLES[role_key]