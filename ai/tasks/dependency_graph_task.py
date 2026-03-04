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
    {{"name":"Child","kind":"Entity"}},
    {{"name":"AgeGroup","kind":"ENUM"}}
  ],
  "edges": [
    {{"from":"Classroom","to":"AgeGroup","type":"USES"}},
    {{"from":"Invoice","to":"InvoiceStatus","type":"USES"}}
  ]
}}

RULES:
- An edge exists if a field type references another type in registry.
- Ignore primitives (String, Integer, BigDecimal, LocalDate, List<...>, etc.)
Return ONLY JSON.
""",
        "expected_output": "JSON dependency graph"
    }