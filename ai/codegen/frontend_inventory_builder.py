"""
FrontendInventoryBuilder
========================
Builds the list of frontend files to generate from a domain model.
Output items have the same shape as backend inventory items so the
same generation loop can handle both.

File descriptions used:
  REACT_SCAFFOLD  — generated once per project (package.json, App.tsx, …)
  TS_MODEL        — TypeScript interface per entity
  REACT_API       — API service per entity
  REACT_LIST      — List component per entity
  REACT_FORM      — Form component per entity
  REACT_PAGE      — Page component per entity
"""

from typing import Dict, List


class FrontendInventoryBuilder:

    def build(self, domain_model: Dict, project_slug: str) -> List[Dict]:
        dm = domain_model.get("domain_model", domain_model)
        modules = dm.get("modules", {})

        # Collect all entities across modules (preserve order)
        entities_seen: dict[str, dict] = {}
        for module_data in modules.values():
            if not isinstance(module_data, dict):
                continue
            for ename in module_data.get("entities", []):
                if isinstance(ename, str) and ename not in entities_seen:
                    entities_seen[ename] = {"name": ename, "fields": []}

        # Enrich with field data from entities list
        for e in dm.get("entities", []):
            if isinstance(e, dict) and e.get("name") in entities_seen:
                entities_seen[e["name"]]["fields"] = e.get("fields", [])

        entities = list(entities_seen.values())

        inventory: List[Dict] = []

        # ----- scaffold files (once per project) -----
        scaffold_paths = [
            "frontend/package.json",
            "frontend/vite.config.ts",
            "frontend/tsconfig.json",
            "frontend/tsconfig.node.json",
            "frontend/index.html",
            "frontend/.env.example",
            "frontend/src/main.tsx",
            "frontend/src/index.css",
            "frontend/src/App.tsx",
        ]
        for path in scaffold_paths:
            inventory.append({
                "path": path,
                "entity": project_slug,
                "description": "REACT_SCAFFOLD",
                "module": None,
                "fields": [],
                "values": [],
                "all_entities": [e["name"] for e in entities],
            })

        # ----- per-entity files -----
        for entity in entities:
            name = entity["name"]
            lower = name[0].lower() + name[1:]
            fields = entity.get("fields", [])

            per_entity = [
                (f"frontend/src/types/{name}.ts",             "TS_MODEL"),
                (f"frontend/src/api/{lower}Api.ts",           "REACT_API"),
                (f"frontend/src/components/{name}/{name}List.tsx", "REACT_LIST"),
                (f"frontend/src/components/{name}/{name}Form.tsx", "REACT_FORM"),
                (f"frontend/src/pages/{name}Page.tsx",        "REACT_PAGE"),
            ]
            for path, desc in per_entity:
                inventory.append({
                    "path": path,
                    "entity": name,
                    "description": desc,
                    "module": None,
                    "fields": fields,
                    "values": [],
                })

        return inventory
