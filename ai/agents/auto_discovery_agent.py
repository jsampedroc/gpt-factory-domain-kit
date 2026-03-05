# ------------------ Value Object Auto Discovery Agent ------------------
class ValueObjectAutoDiscoveryAgent:
    """
    Detects value objects referenced in entities but missing from the
    domain_model.value_objects section. Prevents compile errors like
    'cannot find symbol Address'.
    """

    COMMON_VO_HINTS = {"Address", "Email", "Phone", "Money"}

    def run(self, factory, domain_model):

        dm = domain_model.get("domain_model", domain_model)

        existing = {v.get("name") for v in dm.get("value_objects", [])}

        detected = []

        for entity in dm.get("entities", []):
            for field in entity.get("fields", []):
                t = field.get("type")

                if not isinstance(t, str):
                    continue

                if t in self.COMMON_VO_HINTS and t not in existing:
                    detected.append(t)

        if not detected:
            return domain_model

        factory.log(f"🧠 Auto‑discovered value objects: {detected}")

        for vo in detected:
            dm.setdefault("value_objects", []).append({
                "name": vo,
                "fields": [
                    {"name": "value", "type": "String"}
                ]
            })

        return domain_model