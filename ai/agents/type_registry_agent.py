# ------------------ Type Registry Agent ------------------
class TypeRegistryAgent:
    """
    Builds a registry of known domain types (entities, value objects,
    enums) so later agents can validate references.
    """

    def run(self, factory, domain_model):

        dm = domain_model.get("domain_model", domain_model)

        registry = set()

        for e in dm.get("entities", []):
            registry.add(e.get("name"))

        for vo in dm.get("value_objects", []):
            registry.add(vo.get("name"))

        for en in dm.get("global_enums", []):
            registry.add(en.get("name"))

        factory.type_registry = registry

        factory.log(f"🧠 Type registry built ({len(registry)} types)")

        return domain_model
