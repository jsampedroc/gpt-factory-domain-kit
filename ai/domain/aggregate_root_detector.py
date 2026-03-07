class AggregateRootDetector:

    def detect(self, domain_graph):

        # domain_graph format:
        # {
        #   "entities": [...],
        #   "relations": [{"from": X, "to": Y, ...}]
        # }

        entities = set(domain_graph.get("entities", []))
        incoming = set()

        for rel in domain_graph.get("relations", []):
            target = rel.get("to")
            if target:
                incoming.add(target)

        roots = []

        for e in entities:
            if e not in incoming:
                roots.append(e)

        return roots