"""
UseCaseEnricherAgent
====================
Post-domain-modeling step.
Ensures every module has meaningful use_cases defined.

If the LLM domain model already included use_cases → keeps them.
If a module has none or fewer than 2 → generates sensible business defaults
based on the entity name and its fields.
"""


class UseCaseEnricherAgent:

    QUERY_PREFIXES = ("get", "list", "find", "search")

    def run(self, domain_model: dict) -> dict:
        dm = domain_model.get("domain_model", domain_model)

        modules = dm.get("modules", {})
        entity_map = {e["name"]: e for e in dm.get("entities", []) if e.get("name")}

        # --- Enrich existing modules that have too few use cases ---
        for module_name, module_data in modules.items():
            existing = module_data.get("use_cases", [])
            if len(existing) >= 4:
                continue  # already rich enough

            entity_names = module_data.get("entities", [])
            if not entity_names:
                continue

            primary = entity_names[0]
            entity = entity_map.get(primary, {})
            fields = entity.get("fields", [])

            generated = list(existing)
            existing_names = {uc.get("name", "") for uc in existing}

            for uc in self._build_candidates(primary, fields):
                if uc["name"] not in existing_names and len(generated) < 6:
                    generated.append(uc)
                    existing_names.add(uc["name"])

            module_data["use_cases"] = generated

        # --- Create modules for entities that are NOT in any module ---
        assigned_entities = {
            entity
            for mod_data in modules.values()
            for entity in mod_data.get("entities", [])
        }

        for entity_name, entity_data in entity_map.items():
            if entity_name in assigned_entities:
                continue

            # Derive module name from entity name (e.g. Patient → patient)
            module_name = entity_name[0].lower() + entity_name[1:]
            fields = entity_data.get("fields", [])

            modules[module_name] = {
                "entities": [entity_name],
                "use_cases": self._build_candidates(entity_name, fields),
            }

        dm["modules"] = modules
        return domain_model

    def _build_candidates(self, entity: str, fields: list) -> list:
        """
        Builds meaningful business use cases for an entity.
        Avoids generic CRUD labels — uses domain verbs instead.
        """
        # Derive id input
        id_input = [{"name": f"{entity[0].lower()}{entity[1:]}Id", "type": "UUID"}]

        # Collect non-id scalar inputs (max 4) for create/update commands
        id_field_name = f"{entity[0].lower()}{entity[1:]}Id"
        scalar_inputs = [
            {"name": f["name"], "type": f["type"]}
            for f in fields
            if f.get("name") not in ("id", id_field_name)
            and not str(f.get("type", "")).endswith("Id")
            and not str(f.get("type", "")).startswith("List")
        ][:4]

        return [
            {
                "name": f"Register{entity}",
                "type": "command",
                "description": f"Registers a new {entity} in the system",
                "inputs": scalar_inputs,
                "returns": entity,
            },
            {
                "name": f"Update{entity}",
                "type": "command",
                "description": f"Updates an existing {entity}",
                "inputs": id_input + scalar_inputs,
                "returns": entity,
            },
            {
                "name": f"Deactivate{entity}",
                "type": "command",
                "description": f"Deactivates a {entity} record",
                "inputs": id_input,
                "returns": entity,
            },
            {
                "name": f"Get{entity}ById",
                "type": "query",
                "description": f"Retrieves a {entity} by its identifier",
                "inputs": id_input,
                "returns": entity,
            },
            {
                "name": f"ListAll{entity}s",
                "type": "query",
                "description": f"Returns all {entity} records",
                "inputs": [],
                "returns": f"List<{entity}>",
            },
        ]
