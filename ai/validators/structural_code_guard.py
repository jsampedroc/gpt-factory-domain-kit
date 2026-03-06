import re


class StructuralCodeGuard:
    """
    Prevents hallucinated fields, invalid imports,
    and invalid repository/service relationships.
    """

    FIELD_RE = re.compile(r"private\s+[A-Za-z0-9_<>,\s]+\s+([a-zA-Z0-9_]+)\s*;")
    IMPORT_RE = re.compile(r"import\s+([a-zA-Z0-9_.]+);")

    def validate(self, code: str, spec: dict, base_package: str):

        issues = []

        allowed = set(spec.get("allowed_fields", []))

        fields = set(self.FIELD_RE.findall(code))

        invalid_fields = [f for f in fields if allowed and f not in allowed]

        if invalid_fields:
            issues.append({
                "type": "invalid_fields",
                "fields": invalid_fields
            })

        imports = self.IMPORT_RE.findall(code)

        for imp in imports:

            if imp.startswith(base_package):

                if ".domain.model." not in imp and \
                   ".domain.valueobject." not in imp and \
                   ".domain.shared." not in imp and \
                   ".domain.repository." not in imp and \
                   ".application." not in imp and \
                   ".infrastructure." not in imp:

                    issues.append({
                        "type": "invalid_import",
                        "import": imp
                    })

        return issues