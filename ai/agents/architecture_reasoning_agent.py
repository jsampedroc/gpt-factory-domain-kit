class ArchitectureReasoningAgent:

    def run(self, factory, domain_model):

        dm = domain_model.get("domain_model", domain_model)

        entity_count = len(dm.get("entities", []))
        aggregates = len(dm.get("aggregates", []))

        if aggregates > 3:
            style = "hexagonal"
        elif entity_count > 12:
            style = "modular_monolith"
        else:
            style = "simple"

        return {
            "architecture_style": style
        }