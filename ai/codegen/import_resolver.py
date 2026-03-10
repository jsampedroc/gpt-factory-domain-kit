import re
import json
from pathlib import Path


# Build a map: ClassName -> package path derived from inventory.json
INVENTORY_INDEX = {}

try:
    # inventory is stored inside specs/<project>.json under architecture.file_inventory
    specs_dir = Path("specs")

    if specs_dir.exists():
        for spec_file in specs_dir.glob("*.json"):
            data = json.loads(spec_file.read_text())

            inventory = data.get("architecture", {}).get("file_inventory", [])

            for item in inventory:
                path = item.get("path")

                if path and path.endswith(".java"):
                    class_name = Path(path).stem

                    # base package path from inventory
                    pkg = path.replace(".java", "").replace("/", ".")

                    # if inventory provides module but path is not under modules/
                    module = item.get("module")
                    if module and not pkg.startswith("modules."):
                        # ensure module prefix exists so later normalization works
                        pkg = f"modules.{module}." + pkg if not pkg.startswith(f"{module}.") else f"modules.{pkg}"

                    INVENTORY_INDEX[class_name] = pkg
except Exception:
    # inventory is optional – resolver still works without it
    pass


JAVA_TYPES = {
    "String",
    "Integer",
    "Long",
    "Double",
    "Boolean",
    "int",
    "long",
    "double",
    "float",
    "boolean",
}


JAVA_COLLECTIONS = {
    "List": "java.util.List",
    "Set": "java.util.Set",
    "Map": "java.util.Map",
}


JAVA_TIME_IMPORTS = {
    "LocalDate": "java.time.LocalDate",
    "LocalDateTime": "java.time.LocalDateTime",
    "Instant": "java.time.Instant",
}


JAVA_UTIL_IMPORTS = {
    "UUID": "java.util.UUID",
    "Optional": "java.util.Optional",
}


JAVA_MATH_IMPORTS = {
    "BigDecimal": "java.math.BigDecimal",
}


GENERIC_PATTERN = re.compile(r"<(.+)>")


def _extract_generic_types(type_str: str):
    """
    Extract all inner generic types.

    Examples:
        List<Allergy> -> ["Allergy"]
        Map<String, Allergy> -> ["String", "Allergy"]
        List<Map<String, Child>> -> ["Map<String, Child>", "String", "Child"]
    """

    results = []

    match = GENERIC_PATTERN.search(type_str)

    if not match:
        return results

    inner = match.group(1)

    parts = [p.strip() for p in inner.split(",")]

    for p in parts:
        results.append(p)

        if "<" in p:
            results.extend(_extract_generic_types(p))

    return results


def _extract_outer_type(type_str: str):
    if "<" in type_str:
        return type_str.split("<", 1)[0]
    return type_str


def resolve_imports(code: str, fields: list, base_package: str, module: str):

    imports = set()

    # --- Extra automatic import detection based on generated code ---
    # ValueObject base interface
    if "implements ValueObject" in code:
        imports.add(f"import {base_package}.domain.shared.ValueObject;")

    # java.util.Objects utility
    if "Objects." in code:
        imports.add("import java.util.Objects;")

    # Optional detection
    if "Optional<" in code or " Optional " in code:
        imports.add("import java.util.Optional;")

    # Jakarta validation annotations
    ANNOTATION_IMPORTS = {
        "NotBlank": "jakarta.validation.constraints.NotBlank",
        "NotNull": "jakarta.validation.constraints.NotNull",
        "Past": "jakarta.validation.constraints.Past",
        "PastOrPresent": "jakarta.validation.constraints.PastOrPresent",
        "Future": "jakarta.validation.constraints.Future",
        "FutureOrPresent": "jakarta.validation.constraints.FutureOrPresent",
        "Size": "jakarta.validation.constraints.Size",
        "Email": "jakarta.validation.constraints.Email",
    }

    for ann, imp in ANNOTATION_IMPORTS.items():
        if f"@{ann}" in code:
            imports.add(f"import {imp};")

    # Spring annotations
    if "@Repository" in code:
        imports.add("import org.springframework.stereotype.Repository;")

    package_name = None
    class_name = None

    for line in code.splitlines():
        line = line.strip()
        if line.startswith("package "):
            package_name = line.replace("package ", "").replace(";", "").strip()
        if (
            line.startswith("public class ")
            or line.startswith("public record ")
            or line.startswith("public interface ")
        ):
            parts = line.split()
            if len(parts) >= 3:
                class_name = parts[2].split("(")[0]

    if module:
        domain_model_pkg = f"{base_package}.{module}.domain.model"
    else:
        domain_model_pkg = f"{base_package}.domain.model"

    # value objects belong to the module when available
    if module:
        domain_vo_pkg = f"{base_package}.{module}.domain.valueobject"
    else:
        domain_vo_pkg = f"{base_package}.domain.valueobject"

    # --- Infer additional types from the code itself (methods, annotations, adapters) ---
    # We must ignore common Java/Spring types to avoid generating wrong imports
    IGNORED_TYPES = {
        "List", "Set", "Map", "Optional", "UUID",
        "LocalDate", "LocalDateTime", "Instant",
        "Entity", "Table", "Column",
        "Repository", "Service", "Controller",
        "Override", "Objects", "ValueObject",
        "String", "Integer", "Long", "Double", "Boolean"
    }

    inferred_types = set()

    for line in code.splitlines():
        matches = re.findall(r"\b([A-Z][A-Za-z0-9_]*)\b", line)
        for m in matches:
            if m in IGNORED_TYPES:
                continue
            inferred_types.add(m)

    # Do NOT mutate the original fields list. This was causing duplicated
    # and incorrect imports because inferred types were treated like domain
    # fields. Instead keep them separate.
    inferred_field_types = [{"type": t} for t in inferred_types]

    # repositories should not inherit entity field types
    if package_name and package_name.endswith(".domain.repository"):
        fields_to_process = inferred_field_types
    else:
        fields_to_process = list(fields) + inferred_field_types

    # Prevent importing the class being generated (e.g., ChildRepository importing itself)
    def _is_self_type(t):
        return class_name and t == class_name

    # process both real fields and inferred types without mutating input
    for field in fields_to_process:

        t = field.get("type")

        if not t:
            continue

        outer = _extract_outer_type(t)

        # handle collection imports
        if outer in JAVA_COLLECTIONS:
            imports.add(f"import {JAVA_COLLECTIONS[outer]};")

        # skip collection type itself from further processing
        if outer in JAVA_COLLECTIONS:
            continue

        # resolve generics
        inner_types = _extract_generic_types(t)

        types_to_process = [outer] + inner_types

        for typ in types_to_process:

            typ = _extract_outer_type(typ)

            # skip self type (e.g., interface importing itself)
            if _is_self_type(typ):
                continue

            if typ in JAVA_TIME_IMPORTS:
                imports.add(f"import {JAVA_TIME_IMPORTS[typ]};")
                continue

            if typ in JAVA_UTIL_IMPORTS:
                imports.add(f"import {JAVA_UTIL_IMPORTS[typ]};")
                continue

            if typ in JAVA_MATH_IMPORTS:
                imports.add(f"import {JAVA_MATH_IMPORTS[typ]};")
                continue

            if typ in JAVA_TYPES:
                continue

            # Heuristic resolution for common architecture layers
            if module:
                # domain repositories
                if typ.endswith("Repository"):
                    # avoid self-import and avoid importing repositories already in same package
                    if _is_self_type(typ):
                        continue
                    if package_name and package_name.endswith(".domain.repository"):
                        continue
                    imports.add(f"import {base_package}.{module}.domain.repository.{typ};")
                    continue

                # JPA entities
                if typ.endswith("JpaEntity"):
                    imports.add(f"import {base_package}.{module}.infrastructure.persistence.entity.{typ};")
                    continue

                # Spring Data repositories
                if typ.startswith("SpringData") and typ.endswith("Repository"):
                    imports.add(f"import {base_package}.{module}.infrastructure.persistence.spring.{typ};")
                    continue

                # value objects
                if typ.endswith("Id"):
                    imports.add(f"import {base_package}.{module}.domain.valueobject.{typ};")
                    continue

                # domain models referenced by repositories
                if package_name and package_name.endswith(".domain.repository"):
                    if typ not in JAVA_TYPES and not typ.endswith("Id") and not typ.endswith("Repository"):
                        imports.add(f"import {base_package}.{module}.domain.model.{typ};")
                        continue

                # domain model entities (prefer inventory resolution)
                if typ not in JAVA_TYPES and typ[0].isupper():
                    if typ in INVENTORY_INDEX:
                        pkg = INVENTORY_INDEX[typ]

                        parts = pkg.split(".")
                        if parts and parts[0] == "modules" and len(parts) > 1:
                            pkg = ".".join(parts[1:])

                        if not pkg.endswith(typ):
                            pkg = f"{pkg}.{typ}"

                        if not pkg.startswith(base_package):
                            import_path = f"{base_package}.{pkg}"
                        else:
                            import_path = pkg

                        if package_name and import_path.startswith(package_name):
                            continue

                        imports.add(f"import {import_path};")
                        continue

            # Resolve using inventory.json only (deterministic)
            import_path = None

            if typ in INVENTORY_INDEX:
                pkg = INVENTORY_INDEX[typ]

                # normalize inventory path like modules.child.domain.valueobject.ChildId
                parts = pkg.split(".")
                if parts and parts[0] == "modules" and len(parts) > 1:
                    # keep module name (parts[1]) -> child.domain.valueobject.ChildId
                    pkg = ".".join(parts[1:])

                # if inventory says domain.valueobject but we are inside a module,
                # prefer module-local valueobjects
                if pkg.startswith("domain.valueobject") and module:
                    pkg = f"{module}.{pkg}"

                # ensure class name is included
                if not pkg.endswith(typ):
                    pkg = f"{pkg}.{typ}"

                # ensure base package prefix
                if not pkg.startswith(base_package):
                    import_path = f"{base_package}.{pkg}"
                else:
                    import_path = pkg

            # If we cannot resolve the type, skip it (avoid wrong imports)
            if not import_path:
                continue

            # do not import the class itself
            if class_name and typ == class_name:
                continue

            # avoid importing classes from the same package
            if package_name and import_path.startswith(package_name):
                continue

            imports.add(f"import {import_path};")

    if not imports:
        return code

    lines = code.splitlines()

    insert_index = None

    for i, line in enumerate(lines):
        if line.startswith("package "):
            insert_index = i + 1
            break

    if insert_index is None:
        return code

    # remove existing imports to avoid duplication
    cleaned_lines = [
        line for line in lines if not line.startswith("import ")
    ]

    imports_block = sorted(list(imports))

    new_lines = (
        cleaned_lines[:insert_index]
        + [""]
        + imports_block
        + [""]
        + cleaned_lines[insert_index:]
    )

    return "\n".join(new_lines)