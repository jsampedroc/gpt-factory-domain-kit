"""
CrossFileConsistencyValidator
=============================
Post-generation validator that detects and fixes cross-file inconsistencies
in LLM-generated Java code:

1. Record-style accessor calls on non-record classes
   e.g. `treatment.type()` → `treatment.getType()`

2. Constructor arity mismatches (reported, not auto-fixed)
   e.g. `new Treatment(id, type, desc)` when constructor requires 6 args
"""

import re
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class ClassInfo:
    class_name: str
    is_record: bool
    constructor_arities: list
    getter_names: set
    file_path: Path


class CrossFileConsistencyValidator:

    def __init__(self):
        # Compiled once — reused across all files
        self._re_class_decl = re.compile(
            r"\bpublic\s+(?:final\s+)?(class|record|interface|enum)\s+(\w+)"
        )
        self._re_getter = re.compile(
            r"\bpublic\s+[\w<>\[\], ]+\s+(get\w+)\s*\(\s*\)"
        )
        self._re_import = re.compile(r"\bimport\s+[\w.]+\.(\w+);")
        self._re_new_call = re.compile(r"\bnew\s+(\w+)\s*\(")

    # ------------------------------------------------------------------
    # Public entry point
    # ------------------------------------------------------------------

    def run(self, factory):
        """
        Called from the orchestrator after all files are generated.
        Returns {"accessor_fixes": int, "import_fixes": int, "arity_warnings": list[str]}
        """
        java_root = factory.output_root / "backend" / "src" / "main" / "java"
        if not java_root.exists():
            return {"accessor_fixes": 0, "import_fixes": 0, "arity_warnings": []}

        java_files = list(java_root.rglob("*.java"))
        if not java_files:
            return {"accessor_fixes": 0, "import_fixes": 0, "arity_warnings": []}

        index = self._build_class_index(java_files)

        # Build ground-truth import map from actual files on disk
        ground_truth = self._build_ground_truth_imports(java_files)

        total_accessor_fixes = 0
        total_import_fixes = 0
        all_warnings = []

        for path in java_files:
            try:
                fixes = self._fix_wrong_imports(path, ground_truth)
                total_import_fixes += fixes
            except Exception as e:
                factory.log(f"⚠️ [CONSISTENCY] import fix skipped for {path.name}: {e}")

            try:
                fixes = self._fix_record_accessors(path, index)
                total_accessor_fixes += fixes
            except Exception as e:
                factory.log(f"⚠️ [CONSISTENCY] accessor fix skipped for {path.name}: {e}")

            try:
                warnings = self._report_arity_mismatches(path, index)
                all_warnings.extend(warnings)
                for w in warnings:
                    factory.log(f"⚠️ [CONSISTENCY] {w}")
            except Exception as e:
                factory.log(f"⚠️ [CONSISTENCY] arity check skipped for {path.name}: {e}")

        factory.log(
            f"🔗 Cross-file consistency: {total_import_fixes} import fix(es), "
            f"{total_accessor_fixes} accessor fix(es), "
            f"{len(all_warnings)} arity warning(s)"
        )
        return {
            "accessor_fixes": total_accessor_fixes,
            "import_fixes": total_import_fixes,
            "arity_warnings": all_warnings,
        }

    # ------------------------------------------------------------------
    # Ground-truth import fixer (filesystem-based)
    # ------------------------------------------------------------------

    def _build_ground_truth_imports(self, java_files):
        """
        Scan every .java file and extract its real package declaration.
        Returns: dict[class_name -> "import full.package.ClassName;"]
        """
        ground_truth = {}
        pkg_re = re.compile(r"^\s*package\s+([\w.]+)\s*;", re.MULTILINE)
        class_re = re.compile(
            r"\bpublic\s+(?:final\s+)?(?:class|record|interface|enum)\s+(\w+)"
        )
        for path in java_files:
            try:
                content = path.read_text(encoding="utf-8")
                pkg_m = pkg_re.search(content)
                cls_m = class_re.search(content)
                if pkg_m and cls_m:
                    pkg = pkg_m.group(1)
                    cls = cls_m.group(1)
                    ground_truth[cls] = f"import {pkg}.{cls};"
            except Exception:
                pass
        return ground_truth

    def _fix_wrong_imports(self, path, ground_truth):
        """
        For every import line in the file, if the class name is in ground_truth
        but the import path differs, replace it with the correct one.
        Also adds missing imports for types used in the code body.
        Returns number of fixes made.
        """
        try:
            content = path.read_text(encoding="utf-8")
        except Exception:
            return 0

        original = content
        lines = content.splitlines()
        new_lines = []
        fixes = 0

        # Determine this file's own class name to avoid self-import
        own_cls_m = re.search(
            r"\bpublic\s+(?:final\s+)?(?:class|record|interface|enum)\s+(\w+)", content
        )
        own_class = own_cls_m.group(1) if own_cls_m else None

        # Determine this file's own package
        pkg_m = re.search(r"^\s*package\s+([\w.]+)\s*;", content, re.MULTILINE)
        own_pkg = pkg_m.group(1) if pkg_m else None

        # Fix existing wrong imports
        for line in lines:
            stripped = line.strip()
            if stripped.startswith("import ") and stripped.endswith(";"):
                # Extract class name (last segment)
                import_path = stripped[len("import "):].rstrip(";").strip()
                class_name = import_path.split(".")[-1]
                if (
                    class_name in ground_truth
                    and ground_truth[class_name] != stripped
                    and class_name != own_class
                ):
                    new_lines.append(ground_truth[class_name])
                    fixes += 1
                    continue
            new_lines.append(line)

        content = "\n".join(new_lines)

        # Add missing imports for types referenced in code but not imported
        existing_imports = {
            line.strip()
            for line in content.splitlines()
            if line.strip().startswith("import ")
        }
        existing_classes = {imp.split(".")[-1].rstrip(";") for imp in existing_imports}

        # Find all capitalized type references in the code body (after last import)
        imports_to_add = []
        for class_name, import_stmt in ground_truth.items():
            if class_name == own_class:
                continue
            # skip if already imported
            if class_name in existing_classes:
                continue
            # skip if same package (no import needed)
            if own_pkg and import_stmt == f"import {own_pkg}.{class_name};":
                continue
            # only add if the class name appears as a word in the code
            if re.search(rf"\b{re.escape(class_name)}\b", content):
                imports_to_add.append(import_stmt)
                fixes += 1

        if imports_to_add:
            # Insert after package declaration
            insert_re = re.compile(r"(^\s*package\s+[\w.]+\s*;)", re.MULTILINE)
            m = insert_re.search(content)
            if m:
                insert_pos = m.end()
                block = "\n" + "\n".join(sorted(imports_to_add))
                content = content[:insert_pos] + block + content[insert_pos:]

        if content != original:
            path.write_text(content, encoding="utf-8")

        return fixes

    # ------------------------------------------------------------------
    # Index building
    # ------------------------------------------------------------------

    def _build_class_index(self, java_files):
        index = {}
        for path in java_files:
            try:
                info = self._parse_class_info(path)
                if info and info.class_name not in index:
                    index[info.class_name] = info
            except Exception:
                pass
        return index

    def _parse_class_info(self, path):
        try:
            content = path.read_text(encoding="utf-8")
        except Exception:
            return None

        m = self._re_class_decl.search(content)
        if not m:
            return None

        kind = m.group(1)
        class_name = m.group(2)
        is_record = kind == "record"

        getter_names = set(self._re_getter.findall(content))

        constructor_arities = []
        ctor_pattern = re.compile(
            rf"\bpublic\s+{re.escape(class_name)}\s*\(([^)]*)\)"
        )
        for cm in ctor_pattern.finditer(content):
            arity = self._count_args(cm.group(1))
            constructor_arities.append(arity)

        return ClassInfo(
            class_name=class_name,
            is_record=is_record,
            constructor_arities=constructor_arities,
            getter_names=getter_names,
            file_path=path,
        )

    # ------------------------------------------------------------------
    # Fix: record-style accessors → getters
    # ------------------------------------------------------------------

    def _build_record_variable_map(self, content, index):
        """
        Scan method signatures to build: variable_name -> ClassInfo for record types.
        Example: `execute(RegisterAppointmentCommand command)` → {"command": <record info>}
        """
        record_vars = {}
        # Match method parameters: TypeName varName
        param_re = re.compile(r"\b(\w+)\s+(\w+)\s*[,)]")
        for m in param_re.finditer(content):
            type_name = m.group(1)
            var_name = m.group(2)
            info = index.get(type_name)
            if info and info.is_record:
                record_vars[var_name] = info
        return record_vars

    def _fix_record_accessors(self, path, index):
        content = path.read_text(encoding="utf-8")
        original = content

        # Which classes are imported in this file?
        imported_classes = set(self._re_import.findall(content))

        # Map: variable name → record ClassInfo (to avoid rewriting record-style accessors)
        record_vars = self._build_record_variable_map(content, index)

        fixes = 0
        for class_name, info in index.items():
            # Records use accessor style natively — never rewrite them
            if info.is_record:
                continue
            # Only rewrite if this class is actually imported here
            if class_name not in imported_classes:
                continue
            if not info.getter_names:
                continue

            for getter in info.getter_names:
                field_name = self._field_from_getter(getter)
                if not field_name:
                    continue

                # Only rewrite foo.field() — NOT foo.getField() or foo.setField()
                pattern = re.compile(
                    rf"(\w+)\.({re.escape(field_name)})\(\)"
                )

                def make_replacer(g, record_vars=record_vars):
                    def replacer(m):
                        var = m.group(1)
                        # Don't rewrite if var looks like a class name (capital)
                        if var[0].isupper():
                            return m.group(0)
                        # Don't rewrite if var is a record-typed variable
                        if var in record_vars:
                            return m.group(0)
                        return f"{var}.{g}()"
                    return replacer

                new_content, n = pattern.subn(make_replacer(getter), content)
                if n:
                    content = new_content
                    fixes += n

        if fixes:
            path.write_text(content, encoding="utf-8")

        return fixes

    @staticmethod
    def _field_from_getter(getter_name):
        """'getType' → 'type', 'getCost' → 'cost'"""
        if not getter_name.startswith("get") or len(getter_name) <= 3:
            return None
        rest = getter_name[3:]
        return rest[0].lower() + rest[1:]

    # ------------------------------------------------------------------
    # Report: constructor arity mismatches
    # ------------------------------------------------------------------

    def _report_arity_mismatches(self, path, index):
        content = path.read_text(encoding="utf-8")
        warnings = []

        # Find `new ClassName(` — then count args via depth tracking
        for m in self._re_new_call.finditer(content):
            class_name = m.group(1)
            info = index.get(class_name)
            if not info or not info.constructor_arities:
                continue

            # Extract the argument list with depth tracking
            start = m.end()  # position right after the opening `(`
            args_str = self._extract_balanced(content, start)
            if args_str is None:
                continue

            actual_arity = self._count_args(args_str)

            if actual_arity not in info.constructor_arities:
                warnings.append(
                    f"{path.name}: `new {class_name}` called with {actual_arity} arg(s) "
                    f"but {info.file_path.name} defines constructor(s) with "
                    f"{info.constructor_arities} arg(s)"
                )

        return warnings

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _extract_balanced(content, start):
        """
        Starting right after an opening '(', extract everything up to the
        matching ')' using depth tracking. Returns the inner string or None.
        """
        depth = 1
        i = start
        while i < len(content) and depth > 0:
            c = content[i]
            if c == '(':
                depth += 1
            elif c == ')':
                depth -= 1
            i += 1
        if depth != 0:
            return None
        return content[start:i - 1]

    @staticmethod
    def _count_args(args_str):
        """
        Count top-level comma-separated arguments, respecting nested
        parentheses and angle brackets.
        Returns 0 for empty/whitespace-only strings.
        """
        args_str = args_str.strip()
        if not args_str:
            return 0

        count = 1
        depth = 0
        for ch in args_str:
            if ch in ('(', '<', '[', '{'):
                depth += 1
            elif ch in (')', '>', ']', '}'):
                depth -= 1
            elif ch == ',' and depth == 0:
                count += 1
        return count
