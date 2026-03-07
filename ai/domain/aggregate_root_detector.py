class AggregateRootDetector:

    def detect(self, domain_graph):

        incoming = set()
        nodes = set()

        for src, targets in domain_graph.items():

            nodes.add(src)

            for t in targets:
                incoming.add(t)
                nodes.add(t)

        roots = []

        for node in nodes:
            if node not in incoming:
                roots.append(node)

        return roots