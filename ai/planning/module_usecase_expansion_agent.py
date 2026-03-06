class UseCaseExpansionAgent:

    COMMAND_PATTERNS = [
        "Create{entity}",
        "Update{entity}",
        "Delete{entity}",
        "Activate{entity}",
        "Deactivate{entity}"
    ]

    QUERY_PATTERNS = [
        "Get{entity}",
        "List{entity}",
        "Search{entity}"
    ]

    def run(self, domain_model):

        dm = domain_model.get("domain_model", domain_model)

        entities = dm.get("entities", [])
        aggregates = dm.get("aggregates", [])

        roots = {a["aggregate"] for a in aggregates}

        expanded = []

        for e in entities:

            name = e["name"]

            if name not in roots:
                continue

            for pattern in self.COMMAND_PATTERNS:
                expanded.append({
                    "name": pattern.format(entity=name) + "UseCase",
                    "entity": name,
                    "type": "command"
                })

            for pattern in self.QUERY_PATTERNS:
                expanded.append({
                    "name": pattern.format(entity=name) + "Query",
                    "entity": name,
                    "type": "query"
                })

        dm["expanded_usecases"] = expanded
        return domain_model