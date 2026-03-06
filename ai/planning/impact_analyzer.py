class ImpactAnalyzer:

    def __init__(self, domain_graph):
        self.domain_graph = domain_graph or {}

    def compute_impacted_files(self, inventory, changed_entities):

        impacted = set()

        for item in inventory:
            entity = item.get("entity")

            if entity in changed_entities:
                impacted.add(item["path"])
                continue

            relations = self.domain_graph.get(entity, [])

            if any(rel in changed_entities for rel in relations):
                impacted.add(item["path"])

        return impacted