from typing import Dict, List


class InventoryBuilder:
    """
    Deterministically builds the inventory used by the factory.

    The inventory is the single source of truth for:
      - entity vs value object vs enum
      - module location
      - package resolution

    This avoids LLM hallucinations in later stages (imports, generators, adapters).
    """

    PRIMITIVES = {
        "String", "Integer", "Long", "Boolean", "Double", "Float",
        "Short", "Byte", "Character", "UUID", "LocalDate", "LocalDateTime",
        "List", "Set", "Map", "Optional"
    }

    def build(self, domain_model: Dict, base_package: str) -> List[Dict]:
        """
        Converts a domain model JSON into a deterministic inventory.
        """

        inventory: List[Dict] = []

        modules = domain_model.get("modules", {})

        # 🔴 Fallback: some domain models put entities at root level
        root_entities = domain_model.get("entities", [])
        root_value_objects = domain_model.get("value_objects", [])
        root_enums = domain_model.get("enums", [])

        # Normalize modules to dict form: {name: module_dict}
        if isinstance(modules, list):
            normalized = {}
            for m in modules:
                if isinstance(m, dict) and m.get("name"):
                    normalized[m["name"]] = m
                elif isinstance(m, str):
                    normalized[m] = {
                        "name": m,
                        "entities": [],
                        "value_objects": [],
                        "enums": []
                    }
            modules = normalized

        # Guard: ensure modules is a dict
        if not isinstance(modules, dict):
            modules = {}

        # modules is a dict: {"child": {...}, "parent": {...}}
        for module_name, module in modules.items():

            if not isinstance(module, dict):
                module = {}

            # -------- Entities --------
            for entity in module.get("entities", []):
                if isinstance(entity, str):
                    name = entity
                    fields = []
                else:
                    name = entity.get("name")
                    fields = entity.get("fields", [])

                inventory.append(
                    self._build_item(
                        name=name,
                        module=module_name,
                        description="ENTITY",
                        fields=fields,
                        base_package=base_package,
                        package_suffix="domain.model",
                    )
                )

            # -------- Value Objects --------
            for vo in module.get("value_objects", []):
                if isinstance(vo, str):
                    name = vo
                    fields = []
                else:
                    name = vo.get("name")
                    fields = vo.get("fields", [])

                inventory.append(
                    self._build_item(
                        name=name,
                        module=module_name,
                        description="VALUEOBJECT",
                        fields=fields,
                        base_package=base_package,
                        package_suffix="domain.valueobject",
                    )
                )

            # -------- Enums --------
            for enum in module.get("enums", []):
                if isinstance(enum, str):
                    name = enum
                else:
                    name = enum.get("name")

                inventory.append(
                    self._build_item(
                        name=name,
                        module=module_name,
                        description="ENUM",
                        fields=[],
                        base_package=base_package,
                        package_suffix="domain.shared",
                    )
                )

        # -------- Fallback: root-level entities (no modules) --------
        if not modules and (root_entities or root_value_objects or root_enums):

            module_name = None

            for entity in root_entities:
                if isinstance(entity, str):
                    name = entity
                    fields = []
                else:
                    name = entity.get("name")
                    fields = entity.get("fields", [])

                if not name:
                    continue

                inventory.append(
                    self._build_item(
                        name=name,
                        module=module_name,
                        description="ENTITY",
                        fields=fields,
                        base_package=base_package,
                        package_suffix="domain.model",
                    )
                )

            for vo in root_value_objects:
                if isinstance(vo, str):
                    name = vo
                    fields = []
                else:
                    name = vo.get("name")
                    fields = vo.get("fields", [])

                if not name:
                    continue

                inventory.append(
                    self._build_item(
                        name=name,
                        module=module_name,
                        description="VALUEOBJECT",
                        fields=fields,
                        base_package=base_package,
                        package_suffix="domain.valueobject",
                    )
                )

            for enum in root_enums:
                if isinstance(enum, str):
                    name = enum
                else:
                    name = enum.get("name")

                if not name:
                    continue

                inventory.append(
                    self._build_item(
                        name=name,
                        module=module_name,
                        description="ENUM",
                        fields=[],
                        base_package=base_package,
                        package_suffix="domain.shared",
                    )
                )

        # -------- Global Enums --------
        for enum in domain_model.get("global_enums", []):
            if isinstance(enum, str):
                name = enum
            else:
                name = enum.get("name")

            if not name:
                continue

            inventory.append(
                self._build_item(
                    name=name,
                    module=None,
                    description="ENUM",
                    fields=[],
                    base_package=base_package,
                    package_suffix="domain.shared",
                )
            )

        return inventory

    def _build_item(
        self,
        name: str,
        module: str,
        description: str,
        fields: List[Dict],
        base_package: str,
        package_suffix: str,
    ) -> Dict:
        """
        Creates a deterministic inventory item.
        """

        package = (
            f"{base_package}.{module}.{package_suffix}"
            if module
            else f"{base_package}.{package_suffix}"
        )

        # Build deterministic file path used by the dependency graph
        if module:
            path = f"modules/{module}/{package_suffix.replace('.', '/')}/{name}.java"
        else:
            path = f"{package_suffix.replace('.', '/')}/{name}.java"

        filtered_fields = []

        for field in fields:
            typ = field.get("type")

            if not typ or typ in self.PRIMITIVES:
                filtered_fields.append(field)
                continue

            filtered_fields.append(field)

        if not name:
            raise ValueError("Inventory item without name detected")

        return {
            "entity": name,
            "name": name,
            "kind": description.lower(),
            "module": module,
            "description": description,
            "package": package,
            "path": path,
            "fields": filtered_fields,
        }