# ai/tasks/dependency_graph_task.py

def build_dependency_graph_task(domain_kit="", type_registry="", **kwargs):
    return {
        "agent": "architect",
        "description": f"""
Build a DEPENDENCY GRAPH from the domain model + type registry.

TYPE REGISTRY:
{type_registry}

DOMAIN MODEL:
{domain_kit}

OUTPUT JSON FORMAT:
{{
  "nodes": [
    {{"name":"EntityA","kind":"Entity"}},
    {{"name":"EnumType","kind":"ENUM"}}
  ],
  "edges": [
    {{"from":"EntityA","to":"EnumType","type":"USES"}},
    {{"from":"EntityB","to":"EntityA","type":"USES"}}
  ]
}}

RULES:
- An edge exists if a field type references another type in registry.
- Ignore primitives (String, Integer, BigDecimal, LocalDate, List<...>, etc.)
Return ONLY JSON.
""",
        "expected_output": "JSON dependency graph"
    }