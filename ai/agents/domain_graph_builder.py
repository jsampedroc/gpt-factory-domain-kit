class SemanticCodeGraphBuilder:
    """
    Builds a richer semantic graph so the generator understands
    entity relationships and avoids hallucinated DTO/service fields.
    """

    def build(self, domain_model: dict):

        dm = domain_model.get("domain_model", domain_model)

        entities = {e.get("name") for e in dm.get("entities", [])}

        graph = {}

        for ent in dm.get("entities", []):
            name = ent.get("name")
            relations = []

            for f in ent.get("fields", []):

                t = f.get("type")
                if not t:
                    continue

                # unwrap generics
                if "<" in t and ">" in t:
                    t = t.split("<")[-1].replace(">", "")

                if t in entities and t != name:
                    relations.append({
                        "target": t,
                        "field": f.get("name")
                    })

            graph[name] = relations

        return graph