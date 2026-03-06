# ai/planning/spec_graph_builder.py

class SpecGraphBuilder:
    """
    Builds a structured specification graph from the domain model.
    This gives the LLM a deterministic structural spec for entities.
    """

    def build(self, domain_model: dict):
        dm = domain_model.get("domain_model", domain_model)

        graph = {}

        for ent in dm.get("entities", []):
            name = ent.get("name")
            fields = ent.get("fields", []) or []

            graph[name] = {
                "fields": fields,
                "relations": []
            }

        return graph