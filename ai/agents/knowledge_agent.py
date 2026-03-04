from ai.domain.domain_knowledge_engine import DomainKnowledgeEngine


class KnowledgeAgent:

    def __init__(self):
        self.engine = DomainKnowledgeEngine()

    def run(self, idea, domain_model):
        return self.engine.enrich(idea, domain_model)