JAVA_AUTO_IMPORTS = {
    "List": "java.util.List",
    "Set": "java.util.Set",
    "Map": "java.util.Map",
    "LocalDate": "java.time.LocalDate",
    "LocalDateTime": "java.time.LocalDateTime",
    "UUID": "java.util.UUID"
}

def resolve_imports(code: str):

    imports = []

    for t, imp in JAVA_AUTO_IMPORTS.items():
        if t in code and imp not in code:
            imports.append(f"import {imp};")

    if not imports:
        return code

    lines = code.splitlines()

    for i,l in enumerate(lines):
        if l.startswith("package"):
            insert = i+1
            break
    else:
        return code

    lines = lines[:insert] + [""] + imports + lines[insert:]

    return "\n".join(lines)