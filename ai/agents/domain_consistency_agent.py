class DomainConsistencyAgent:
    """
    Ensures domain model consistency before code generation.
    Fixes common issues like missing value objects or duplicate standard types.
    """

    STANDARD_TYPES = {
        "UUID",
        "String",
        "Integer",
        "Long",
        "Boolean",
        "BigDecimal",
        "LocalDate",
        "LocalDateTime",
        "DayOfWeek"
    }

    def run(self, factory, domain_model):

        dm = domain_model.get("domain_model", domain_model)

        value_objects = {vo["name"] for vo in dm.get("value_objects", [])}

        detected_missing = set()

        for entity in dm.get("entities", []):
            for field in entity.get("fields", []):

                t = field["type"]

                if (
                    t not in self.STANDARD_TYPES
                    and t not in value_objects
                ):
                    detected_missing.add(t)

        if detected_missing:

            factory.log(
                f"🧠 DomainConsistencyAgent detected missing types: {detected_missing}"
            )

            dm.setdefault("value_objects", [])

            for name in detected_missing:

                dm["value_objects"].append({
                    "name": name,
                    "fields": [
                        {"name": "value", "type": "String"}
                    ]
                })

                factory.log(f"🔧 Auto-created ValueObject: {name}")

        return domain_model