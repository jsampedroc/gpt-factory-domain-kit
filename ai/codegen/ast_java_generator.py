class ASTJavaGenerator:

    def __init__(self, value_objects=None):
        from .java_type_resolver import JavaTypeResolver
        self.resolver = JavaTypeResolver(value_objects=value_objects)

    def set_value_objects(self, value_objects):
        from .java_type_resolver import JavaTypeResolver
        self.resolver = JavaTypeResolver(value_objects=value_objects)

    JAVA_STD_IMPORTS = {
        "LocalDate": "java.time.LocalDate",
        "LocalDateTime": "java.time.LocalDateTime",
        "Instant": "java.time.Instant",
        "List": "java.util.List",
        "Set": "java.util.Set",
        "Map": "java.util.Map",
        "UUID": "java.util.UUID",
        "BigDecimal": "java.math.BigDecimal",
    }

    def _split_generic(self, t):
        """
        Safe generic parser:
        List<Child> -> ("List", ["Child"])
        Map<String, Child> -> ("Map", ["String","Child"])
        """
        outer, inner = t.split("<", 1)
        inner = inner.rsplit(">", 1)[0]
        parts = [p.strip() for p in inner.split(",")]
        return outer.strip(), parts

    def generate_class(self, package_name, class_name, fields, base_package=None, module=None):

        entity_id_type = f"{class_name}Id"

        # Avoid duplicated IDs
        has_id = any(
            f.get("name") == "id" or f.get("name", "").endswith("Id")
            for f in fields
        )

        if not has_id:
            fields = [{"name": "id", "type": entity_id_type}] + list(fields)

        imports = set()

        for f in fields:

            t = f.get("type", "")
            if not t:
                continue

            # Handle generic types like List<Child>
            if "<" in t:

                outer, inner_types = self._split_generic(t)

                # Resolve standard Java imports
                if outer in self.JAVA_STD_IMPORTS:
                    imports.add(self.JAVA_STD_IMPORTS[outer])
                else:
                    imp = self.resolver.resolve(outer, base_package, module)
                    if imp and not imp.startswith(package_name):
                        imports.add(imp)

                for inner in inner_types:

                    if inner in self.JAVA_STD_IMPORTS:
                        imports.add(self.JAVA_STD_IMPORTS[inner])
                        continue

                    imp = self.resolver.resolve(inner, base_package, module)
                    if imp and not imp.startswith(package_name):
                        imports.add(imp)

            else:

                # Standard Java types
                if t in self.JAVA_STD_IMPORTS:
                    imports.add(self.JAVA_STD_IMPORTS[t])
                    continue

                imp = self.resolver.resolve(t, base_package, module)
                if imp and not imp.startswith(package_name):
                    imports.add(imp)

        lines = []

        lines.append(f"package {package_name};\n")

        if imports:
            lines.append("\n")
            for imp in sorted(imports):
                lines.append(f"import {imp};\n")

        lines.append("\n")

        record_fields = []
        for f in fields:
            t = f.get("type", "Object")
            n = f.get("name", "field")
            record_fields.append(f"{t} {n}")

        field_signature = ",\n        ".join(record_fields)

        lines.append(f"public record {class_name}(\n")
        lines.append(f"        {field_signature}\n")
        lines.append(") {}\n")

        return "".join(lines)
