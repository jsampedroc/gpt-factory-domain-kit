class AggregateLifecycleAgent:
    """
    Generates lifecycle commands for aggregate roots using structural
    information only (no domain keywords).

    Strategy:
    1. Each aggregate root receives basic lifecycle operations.
    2. Members of the aggregate produce association operations.
    3. Operations are generated deterministically so the pipeline
       stays reproducible.
    """

    CORE_PATTERNS = [
        "Create{root}",
        "Update{root}",
        "Deactivate{root}",
        "Delete{root}"
    ]

    RELATION_PATTERNS = [
        "Attach{member}To{root}",
        "Detach{member}From{root}"
    ]

    def run(self, domain_model):

        dm = domain_model.get("domain_model", domain_model)

        aggregates = dm.get("aggregates", [])

        usecases = []

        for agg in aggregates:

            root = agg.get("aggregate") or agg.get("root")
            members = agg.get("entities", [])

            if not root:
                continue

            # Generate core lifecycle commands
            for pattern in self.CORE_PATTERNS:
                usecases.append({
                    "name": pattern.format(root=root),
                    "entity": root,
                    "aggregate": root,
                    "type": "command"
                })

            # Generate relationship commands
            for member in members:

                if member == root:
                    continue

                for pattern in self.RELATION_PATTERNS:
                    usecases.append({
                        "name": pattern.format(member=member, root=root),
                        "entity": root,
                        "member": member,
                        "aggregate": root,
                        "type": "command"
                    })

        return usecases