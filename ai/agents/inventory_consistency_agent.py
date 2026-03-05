# ------------------ Inventory Consistency Agent ------------------
class InventoryConsistencyAgent:
    """
    Ensures that every referenced domain type (Entity, ValueObject, Enum)
    exists in the inventory before code generation. This prevents DTOs or
    entities referencing types that were never generated.
    """

    TYPE_PATTERN = re.compile(r"\b([A-Z][A-Za-z0-9_]+)\b")

    def run(self, factory, domain_model):

        dm = domain_model.get("domain_model", domain_model)

        known_types = set()

        for e in dm.get("entities", []):
            known_types.add(e.get("name"))

        for vo in dm.get("value_objects", []):
            known_types.add(vo.get("name"))

        for en in dm.get("global_enums", []):
            known_types.add(en.get("name"))

        repaired = False

        for entity in dm.get("entities", []):
            for field in entity.get("fields", []):
                t = field.get("type")

                if not isinstance(t, str):
                    continue

                if t not in known_types and t[0].isupper() and t not in STANDARD_JAVA_TYPES:
                    factory.log(f"🧠 InventoryConsistency: synthesizing missing ValueObject '{t}'")

                    dm.setdefault("value_objects", []).append({
                        "name": t,
                        "fields": [
                            {"name": "value", "type": "String"}
                        ]
                    })

                    known_types.add(t)
                    repaired = True

        if repaired:
            factory.log("🧠 InventoryConsistencyAgent repaired missing domain types")

        return domain_model