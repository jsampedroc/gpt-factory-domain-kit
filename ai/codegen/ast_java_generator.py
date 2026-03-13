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

    JAVA_LANG_TYPES = {"String", "Integer", "Long", "Double", "Float", "Boolean"}

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

        imports = set()

        is_domain_entity = ".domain.model" in package_name

        if is_domain_entity:
            entity_id_type = f"{class_name}Id"

            has_id = any(f.get("name") == "id" for f in fields)

            if not has_id:
                fields = [{"name": "id", "type": entity_id_type}] + list(fields)

            if base_package:
                imp = self.resolver.resolve(entity_id_type, base_package, module)
                if imp:
                    imports.add(imp)

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

                    if inner in self.JAVA_LANG_TYPES:
                        continue

                    if inner in self.JAVA_STD_IMPORTS:
                        imports.add(self.JAVA_STD_IMPORTS[inner])
                        continue

                    imp = self.resolver.resolve(inner, base_package, module)

                    if not imp and base_package and inner[0].isupper():
                        # fallback to domain.model when resolver cannot decide
                        if module:
                            imp = f"{base_package}.{module}.domain.model.{inner}"
                        else:
                            imp = f"{base_package}.domain.model.{inner}"

                    if imp and not imp.startswith(package_name) and inner != class_name:
                        imports.add(imp)

            else:

                # Skip java.lang
                if t in self.JAVA_LANG_TYPES:
                    continue

                # Standard Java imports
                if t in self.JAVA_STD_IMPORTS:
                    imports.add(self.JAVA_STD_IMPORTS[t])
                    continue

                imp = self.resolver.resolve(t, base_package, module)

                if not imp and base_package and t[0].isupper():
                    # fallback to domain.model when resolver cannot decide
                    if module:
                        imp = f"{base_package}.{module}.domain.model.{t}"
                    else:
                        imp = f"{base_package}.domain.model.{t}"

                if imp and not imp.startswith(package_name) and t != class_name:
                    imports.add(imp)

        # --- ValueObject automatic imports ---
        if ".domain.valueobject" in package_name and base_package:
            imports.add(f"{base_package}.domain.shared.ValueObject")
            imports.add("java.util.Objects")

        lines = []

        lines.append(f"package {package_name};\n")

        if imports:
            lines.append("\n")

        if is_domain_entity:
            id_type = f"{class_name}Id"

            if base_package:
                imports.add(f"{base_package}.domain.shared.Entity")

            entity_fields = []
            ctor_fields = []

            for f in fields:
                t = f.get("type", "Object")
                n = f.get("name", "field")

                if n == "id":
                    continue

                entity_fields.append((t, n))
                ctor_fields.append((t, n))

            # Rebuild import section now that Entity import may have been added
            lines = []
            lines.append(f"package {package_name};\n")

            if imports:
                lines.append("\n")
                for imp in sorted(imports):
                    lines.append(f"import {imp};\n")

            lines.append("\n")
            lines.append(f"public class {class_name} extends Entity<{id_type}> {{\n\n")

            for t, n in entity_fields:
                lines.append(f"    private final {t} {n};\n")

            lines.append("\n")

            ctor_params = [f"{id_type} id"] + [f"{t} {n}" for t, n in ctor_fields]
            lines.append(f"    public {class_name}(")
            lines.append(", ".join(ctor_params))
            lines.append(") {\n")
            lines.append("        super(id);\n")
            for _, n in ctor_fields:
                lines.append(f"        this.{n} = {n};\n")
            lines.append("    }\n")

            for t, n in entity_fields:
                method = n[0].upper() + n[1:]
                lines.append(f"\n    public {t} get{method}() {{ return this.{n}; }}\n")

            lines.append("\n}\n")
            return "".join(lines)

        if imports:
            for imp in sorted(imports):
                lines.append(f"import {imp};\n")

        lines.append("\n")

        is_value_object = ".domain.valueobject" in package_name

        if is_value_object:

            lines.append(f"public class {class_name} {{\n\n")

            vo_fields = []
            for f in fields:
                t = f.get("type", "Object")
                n = f.get("name", "field")
                vo_fields.append((t, n))
                lines.append(f"    private final {t} {n};\n")

            lines.append("\n")

            ctor_params = ", ".join([f"{t} {n}" for t, n in vo_fields])
            lines.append(f"    public {class_name}({ctor_params}) {{\n")
            for _, n in vo_fields:
                lines.append(f"        this.{n} = {n};\n")
            lines.append("    }\n")

            for t, n in vo_fields:
                method = n[0].upper() + n[1:]
                lines.append(f"\n    public {t} get{method}() {{ return this.{n}; }}\n")

            lines.append("\n}\n")
            return "".join(lines)

        # DTO / other classes remain records
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
