# ------------------ Import Resolution Agent ------------------
class ImportResolutionAgent:
    """
    Scans generated Java files and automatically injects missing imports
    for domain ValueObjects, Entities and Enums referenced in the code.
    This prevents compile errors like 'cannot find symbol Address'.
    """

    TYPE_PATTERN = re.compile(r"\b([A-Z][A-Za-z0-9_]+)\b")

    def run(self, factory, inventory):

        base_pkg = factory.base_package

        # Build type -> package index from inventory
        type_index = {}

        for item in inventory:
            path = item.get("path")
            name = Path(path).stem
            pkg = factory._expected_package_for(path)
            type_index[name] = pkg

        for item in inventory:

            rel = item["path"]
            file_path = factory.resolve_output_path(rel)

            if not file_path.exists():
                continue

            try:
                content = file_path.read_text(encoding="utf-8")
            except Exception:
                continue

            if "package " not in content:
                continue

            used_types = set(self.TYPE_PATTERN.findall(content))

            missing_imports = []

            for t in used_types:
                if t in type_index and f"import {type_index[t]}.{t};" not in content:

                    # avoid self import
                    expected_pkg = factory._expected_package_for(rel)
                    if type_index[t] == expected_pkg:
                        continue

                    missing_imports.append(f"import {type_index[t]}.{t};")

            if not missing_imports:
                continue

            lines = content.splitlines()

            insert_index = None
            for i, line in enumerate(lines):
                if line.startswith("package "):
                    insert_index = i + 1
                    break

            if insert_index is None:
                continue

            for imp in missing_imports:
                lines.insert(insert_index, imp)
                insert_index += 1

            new_content = "\n".join(lines)

            try:
                file_path.write_text(new_content, encoding="utf-8")
                factory.log(f"🔧 Auto-imports injected in {Path(rel).name}")
            except Exception:
                pass