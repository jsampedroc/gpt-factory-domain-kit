import re


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

    package_name = None
    class_name = None

    for line in code.splitlines():
        line = line.strip()
        if line.startswith("package "):
            package_name = line.replace("package ", "").replace(";", "").strip()
        if line.startswith("public class ") or line.startswith("public record "):
            parts = line.split()
            if len(parts) >= 3:
                class_name = parts[2].split("(")[0]

    if module:
        domain_model_pkg = f"{base_package}.{module}.domain.model"
        domain_vo_pkg = f"{base_package}.{module}.domain.valueobject"
    else:
        domain_model_pkg = f"{base_package}.domain.model"
        domain_vo_pkg = f"{base_package}.domain.valueobject"

    for field in fields:

        t = field.get("type")

        if not t:
            continue

        outer = _extract_outer_type(t)

        # handle collection imports
        if outer in JAVA_COLLECTIONS:
            imports.add(f"import {JAVA_COLLECTIONS[outer]};")

        # resolve generics
        inner_types = _extract_generic_types(t)

        types_to_process = [outer] + inner_types

        for typ in types_to_process:

            typ = _extract_outer_type(typ)

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

            if typ.endswith("Id"):
                imports.add(f"import {domain_vo_pkg}.{typ};")
                continue

            if typ not in JAVA_COLLECTIONS and typ not in JAVA_TYPES:
                if typ and typ[0].isupper():

                    # do not import the class itself
                    if class_name and typ == class_name:
                        continue

                    import_path = f"{domain_model_pkg}.{typ}"

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