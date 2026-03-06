from collections import defaultdict
import re


class DomainGraphBuilder:
    """
    Builds a simple relationship graph between entities based on field types.
    """

    def build(self, domain_model: dict):

        dm = domain_model.get("domain_model", domain_model)

        entities = {e["name"] for e in dm.get("entities", [])}
        graph = defaultdict(set)

        for ent in dm.get("entities", []):
            src = ent.get("name")

            for f in ent.get("fields", []):
                t = f.get("type")

                if not t:
                    continue

                # unwrap generics
                t = re.sub(r".*<(.+?)>", r"\1", t)
                t = t.split(",")[-1].strip()

                if t in entities and t != src:
                    graph[src].add(t)

        return {k: sorted(v) for k, v in graph.items()}