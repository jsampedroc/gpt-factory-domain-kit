import re


class FieldValidator:
    """
    Validates that generated entity/DTO code does not introduce fields
    outside the deterministic specification.
    This reduces LLM hallucinations in generated classes.
    """

    FIELD_RE = re.compile(r"private\s+[A-Za-z0-9_<>,\s]+\s+([a-zA-Z0-9_]+)\s*;")

    def validate(self, code: str, deterministic_spec: dict):

        if not deterministic_spec:
            return True, []

        allowed = set(deterministic_spec.get("allowed_fields", []))

        if not allowed:
            return True, []

        found = set(self.FIELD_RE.findall(code))

        invalid = [f for f in found if f not in allowed]

        return len(invalid) == 0, invalid