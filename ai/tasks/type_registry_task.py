# ai/tasks/type_registry_task.py

def build_type_registry_task(domain_kit="", **kwargs):
    return {
        "agent": "architect",
        "description": f"""
Build a TYPE REGISTRY from this domain model.

DOMAIN MODEL:
{domain_kit}

RULES:
- entities: take domain_model.entities[*].name
- value_objects: take domain_model.value_objects[*].name
- enums: take domain_model.global_enums[*].name

Return ONLY valid JSON:
{{
  "entities": ["..."],
  "value_objects": ["..."],
  "enums": ["..."]
}}
""",
        "expected_output": "JSON type registry"
    }