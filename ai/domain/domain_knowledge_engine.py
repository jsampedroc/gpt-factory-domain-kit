import json
from pathlib import Path


class DomainKnowledgeEngine:

    def __init__(self):

        path = Path("ai/knowledge/domain_patterns.json")

        if path.exists():
            self.patterns = json.loads(path.read_text())
        else:
            self.patterns = {}

    def enrich(self, idea: str, domain_model: dict):

        idea_lower = idea.lower()

        for domain, data in self.patterns.items():

            if any(k in idea_lower for k in data["keywords"]):

                domain_model.setdefault("knowledge", {})[domain] = data

                domain_model.setdefault("entities", [])

                for e in data.get("entities", []):
                    if not any(ent["name"] == e for ent in domain_model["entities"]):
                        domain_model["entities"].append({
                            "name": e,
                            "fields": []
                        })

        return domain_model