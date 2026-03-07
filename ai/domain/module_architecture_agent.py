# ai/domain/module_architecture_agent.py

class ModuleArchitectureAgent:
    """
    Groups entities into logical modules using detected bounded contexts.

    Design goals:
    - domain‑agnostic
    - bounded context → module mapping
    - deterministic fallback when contexts are not present

    Example structure produced:

        modules/
            module_a/
            module_b/
    """

    def run(self, domain_model):

        dm = domain_model.get("domain_model", domain_model)

        entities = dm.get("entities", [])
        contexts = dm.get("bounded_contexts", [])

        modules = {}

        # Map entity names for validation
        entity_names = {e.get("name") for e in entities if e.get("name")}

        if contexts:
            for ctx in contexts:

                name = ctx.get("name")
                ctx_entities = ctx.get("entities", [])

                if not name:
                    continue

                # keep only valid entity names
                filtered_entities = [e for e in ctx_entities if e in entity_names]

                if not filtered_entities:
                    continue

                modules[name.lower()] = {
                    "entities": filtered_entities
                }

        # deterministic fallback
        if not modules:
            modules["core"] = {
                "entities": sorted(entity_names)
            }

        dm["modules"] = modules

        return domain_model