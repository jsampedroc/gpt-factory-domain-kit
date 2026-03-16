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
        "Short", "Byte", "Character", "UUID", "LocalDate", "LocalDateTime"
    }

    def build(self, domain_model: Dict, base_package: str) -> List[Dict]:
        """
        Converts a domain model JSON into a deterministic inventory.
        """

        inventory: List[Dict] = []

        modules = domain_model.get("modules", {})

        # modules is a dict: {"child": {...}, "parent": {...}}
        for module_name, module in modules.items():

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

        package = f"{base_package}.{module}.{package_suffix}" if module else f"{base_package}.{package_suffix}"

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

        return {
            "entity": name,
            "name": name,
            "module": module,
            "description": description,
            "package": package,
            "path": path,
            "fields": filtered_fields,
        }