import hashlib
import json


class DeterministicSpecGenerator:

    def build(self, domain_model: dict):
        dm = domain_model.get("domain_model", domain_model)

        spec = {}

        entities = sorted(dm.get("entities", []), key=lambda e: e.get("name", ""))

        for ent in entities:
            fields = sorted(ent.get("fields", []) or [], key=lambda f: f.get("name", ""))
            name = ent.get("name")

            field_names = [f.get("name") for f in fields if f.get("name")]
            field_types = [f.get("type") for f in fields if f.get("type")]

            try:
                entity_hash = hashlib.sha256(
                    json.dumps(fields, sort_keys=True).encode()
                ).hexdigest()
            except Exception:
                entity_hash = None

            spec[name] = {
                "entity": name,
                "signature": entity_hash,
                "fields": [
                    {
                        "name": f.get("name"),
                        "type": f.get("type"),
                        "required": f.get("required", False)
                    }
                    for f in fields
                ],
                "field_names": field_names,
                "field_types": field_types,
                "allowed_fields": field_names,
                "required_fields": ["id"] if "id" in field_names else []
            }

        return spec