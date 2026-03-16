class UseCasePlannerAgent:
    """
    Converts business capabilities into application use cases in a
    completely domain‑agnostic way.

    Design goals:
    - capability → use case
    - automatic command / query detection
    - aggregate awareness
    - module inference from bounded contexts (if present)
    - no domain specific examples or entity names
    """

    QUERY_PREFIXES = ["get", "list", "find", "search", "load", "fetch"]

    def _is_query(self, name: str) -> bool:
        if not name:
            return False
        return any(name.lower().startswith(p) for p in self.QUERY_PREFIXES)

    def _detect_module(self, entity: str, bounded_contexts: dict):
        """
        Determines the module/bounded context for an entity.

        Strategy:
        1. If bounded contexts exist → find which one owns the entity
        2. Otherwise fallback to a neutral module name
        """

        if not entity:
            return "core"

        # bounded_contexts may be a dict {name: {...}} or a list [{name:..., entities:[...]}, ...]
        if isinstance(bounded_contexts, dict):
            for ctx_name, ctx_data in bounded_contexts.items():
                entities = ctx_data.get("entities", [])
                if entity in entities:
                    return ctx_name

        elif isinstance(bounded_contexts, list):
            for ctx in bounded_contexts:
                ctx_name = ctx.get("name") or ctx.get("bounded_context") or "core"
                entities = ctx.get("entities", [])
                if entity in entities:
                    return ctx_name

        return "core"

    def run(self, domain_model, capabilities):

        dm = domain_model.get("domain_model", domain_model)

        entities = dm.get("entities", [])
        aggregates = dm.get("aggregates", [])
        bounded_contexts = dm.get("bounded_contexts", {})

        # ------------------------------------------------
        # Build aggregate map (entity -> aggregate root)
        # ------------------------------------------------
        aggregate_map = {}

        for agg in aggregates:
            root = agg.get("aggregate") or agg.get("root")
            members = agg.get("entities", [])

            for m in members:
                aggregate_map[m] = root

        usecases = []

        for cap in capabilities:

            name = cap.get("name")
            entity = cap.get("entity")

            if not name:
                continue

            aggregate = aggregate_map.get(entity, entity)

            module = self._detect_module(entity, bounded_contexts)

            if self._is_query(name):

                query_name = f"{name}Query"
                handler_name = f"{name}QueryHandler"

                usecases.append({
                    "name": handler_name,
                    "query": query_name,
                    "entity": entity,
                    "aggregate": aggregate,
                    "module": module,
                    "capability": name,
                    "type": "query"
                })

            else:

                command_name = f"{name}Command"
                usecase_name = f"{name}UseCase"

                usecases.append({
                    "name": usecase_name,
                    "command": command_name,
                    "entity": entity,
                    "aggregate": aggregate,
                    "module": module,
                    "capability": name,
                    "type": "command"
                })

        return usecases