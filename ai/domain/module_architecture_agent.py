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

        # If bounded contexts exist, convert them to modules
        if contexts:

            for ctx in contexts:

                name = ctx.get("name")
                ents = ctx.get("entities", [])

                if not name:
                    continue

                modules[name] = {
                    "entities": ents
                }

        else:
            # fallback: single neutral module
            modules["core"] = {
                "entities": [e.get("name") for e in entities]
            }

        dm["modules"] = modules

        return domain_model