class CodePlanner:

    def build(self, domain_model: dict):
        dm = domain_model.get("domain_model", domain_model)

        entities = dm.get("entities", [])
        aggregates = dm.get("aggregates", [])
        usecases = dm.get("usecases", [])

        plan = {}

        # ------------------------------------------------
        # ENTITY PLANNING
        # ------------------------------------------------
        for ent in entities:
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
            root = agg.get("root")
            members = agg.get("entities", [])

            for m in members:
                aggregate_map[m] = root

        # ------------------------------------------------
        # USE CASE PLANNING
        # ------------------------------------------------
        uc_plan = []

        for uc in usecases:

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
                    "command": f"application/command/{command}.java" if command else None
                }
            })

        if uc_plan:
            plan["__usecases__"] = uc_plan

        return plan