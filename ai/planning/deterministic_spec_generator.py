import hashlib
import json


class DeterministicSpecGenerator:

    def build(self, domain_model: dict):
        dm = domain_model.get("domain_model", domain_model)

        spec = {}

        for ent in dm.get("entities", []):
            name = ent.get("name")
            fields = ent.get("fields", []) or []

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