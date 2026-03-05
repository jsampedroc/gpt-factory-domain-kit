# ------------------ Enum Type Resolver Agent ------------------
class EnumTypeResolverAgent:
    """
    Resolves conflicts between domain enums and Java standard enums
    (example: DayOfWeek vs java.time.DayOfWeek).
    Ensures domain.shared enums are consistently used in the domain model.
    """

    STANDARD_ENUM_CONFLICTS = {
        "DayOfWeek": "java.time.DayOfWeek"
    }

    def run(self, factory, domain_model):

        dm = domain_model.get("domain_model", domain_model)

        domain_enums = {e.get("name") for e in dm.get("global_enums", [])}

        for entity in dm.get("entities", []):
            for field in entity.get("fields", []):
                t = field.get("type")

                if not isinstance(t, str):
                    continue

                if t in self.STANDARD_ENUM_CONFLICTS and t in domain_enums:
                    factory.log(f"🧠 Resolving enum conflict: {t} -> domain.shared.{t}")
                    field["type"] = t

        return domain_model
