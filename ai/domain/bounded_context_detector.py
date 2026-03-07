class BoundedContextDetector:

    """
    Detects bounded contexts using aggregate structure.

    Improvements over the previous implementation:
    - Prevents an entity from belonging to multiple contexts
    - Guarantees deterministic ordering
    - Handles missing aggregates safely
    - Normalizes entity names
    """

    def detect(self, domain_model):

        dm = domain_model.get("domain_model", domain_model)

        entities = dm.get("entities", [])
        aggregates = dm.get("aggregates", [])

        contexts = {}
        entity_owner = {}

        # ------------------------------------------------
        # Build contexts from aggregates
        # ------------------------------------------------

        for agg in aggregates:

            root = agg.get("aggregate") or agg.get("root")
            members = agg.get("entities", [])

            if not root:
                continue

            ctx_name = root.lower()

            contexts.setdefault(ctx_name, set())

            # assign root
            if root not in entity_owner:
                contexts[ctx_name].add(root)
                entity_owner[root] = ctx_name

            # assign members
            for m in members:

                if not m:
                    continue

                # prevent entity from appearing in multiple contexts
                if m in entity_owner:
                    continue

                contexts[ctx_name].add(m)
                entity_owner[m] = ctx_name

        # ------------------------------------------------
        # Fallback if no aggregates exist
        # ------------------------------------------------

        if not contexts and entities:

            contexts["core"] = set()

            for e in entities:
                name = e.get("name")
                if name:
                    contexts["core"].add(name)

        # ------------------------------------------------
        # Normalize deterministic structure
        # ------------------------------------------------

        dm["bounded_contexts"] = sorted(
            [
                {
                    "name": ctx,
                    "entities": sorted(list(ents))
                }
                for ctx, ents in contexts.items()
            ],
            key=lambda c: c["name"]
        )

        return domain_model