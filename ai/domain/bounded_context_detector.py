class BoundedContextDetector:

    """
    Detects bounded contexts using structural heuristics instead of
    domain-specific keywords.

    Strategy:
    1. Each aggregate root defines a potential bounded context.
    2. All entities belonging to that aggregate become part of that context.
    3. If no aggregates exist, fallback to a single neutral context ("core").
    """

    def detect(self, domain_model):

        dm = domain_model.get("domain_model", domain_model)

        entities = dm.get("entities", [])
        aggregates = dm.get("aggregates", [])

        contexts = {}

        # Build contexts from aggregates
        for agg in aggregates:

            root = agg.get("aggregate") or agg.get("root")
            members = agg.get("entities", [])

            if not root:
                continue

            ctx_name = root.lower()

            contexts.setdefault(ctx_name, set()).add(root)

            for m in members:
                contexts[ctx_name].add(m)

        # Fallback if no aggregates detected
        if not contexts and entities:

            contexts["core"] = {e.get("name") for e in entities if e.get("name")}

        # Normalize structure
        dm["bounded_contexts"] = [
            {
                "name": ctx,
                "entities": sorted(list(ents))
            }
            for ctx, ents in contexts.items()
        ]

        return domain_model