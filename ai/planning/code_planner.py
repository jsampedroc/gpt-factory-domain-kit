class CodePlanner:

    def build(self, domain_model: dict):
        dm = domain_model.get("domain_model", domain_model)

        entities = dm.get("entities", [])
        aggregates = dm.get("aggregates", [])
        # usecases may be stored in different places depending on pipeline stage
        usecases = (
            dm.get("usecases")
            or domain_model.get("usecases")
            or dm.get("planned_usecases")
            or domain_model.get("planned_usecases")
            or []
        )
        if not isinstance(usecases, list):
            usecases = []

        plan = {}

        # ------------------------------------------------
        # ENTITY PLANNING
        # ------------------------------------------------
        for ent in entities:
            # allow both dict and string entity representations
            if isinstance(ent, str):
                name = ent
                fields = []
            else:
                name = ent.get("name")
                fields = ent.get("fields", []) or []

            plan[name] = {
                "entity": name,
                "fields": fields,
                "has_id": any(f.get("name") == "id" for f in fields),
                "has_relations": any("Id" in (f.get("type") or "") for f in fields),
            }

        # ------------------------------------------------
        # AGGREGATE MAP (entity -> aggregate root)
        # ------------------------------------------------
        aggregate_map = {}

        for agg in aggregates:
            if isinstance(agg, str):
                continue
            root = agg.get("root")
            members = agg.get("entities", []) or []

            for m in members:
                aggregate_map[m] = root

        # ------------------------------------------------
        # USE CASE PLANNING
        # ------------------------------------------------
        uc_plan = []

        for uc in usecases:

            if isinstance(uc, str):
                uc_name = uc
                entity = None
                command = None
            else:
                uc_name = uc.get("name")
                entity = uc.get("entity")
                command = uc.get("command")

            aggregate = aggregate_map.get(entity, entity)

            uc_plan.append({
                "usecase": uc_name,
                "entity": entity,
                "aggregate": aggregate,
                "command": command,
                "files": {
                    "usecase": f"application/usecase/{uc_name}.java",
                    "command": f"application/command/{command}.java" if command else None,

                    # additional generated backend components
                    "service": f"application/service/{entity}Service.java" if entity else None,
                    "controller": f"api/controller/{entity}Controller.java" if entity else None,
                    "mapper": f"api/mapper/{entity}Mapper.java" if entity else None,

                    "request": f"api/dto/{entity}Request.java" if entity else None,
                    "response": f"api/dto/{entity}Response.java" if entity else None
                }
            })

        if uc_plan:
            # store under a standard key expected by later planners
            plan["usecases"] = uc_plan

        return plan