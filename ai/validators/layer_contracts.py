# ai/validators/layer_contracts.py
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional
import re
import fnmatch
import yaml


# =========================
# Models
# =========================

@dataclass(frozen=True)
class ContractViolation:
    rule: str
    detail: str


# =========================
# Layer Contracts
# =========================

class LayerContracts:
    """
    Contract-first validator for Hexagonal Architecture.

    Enforces:
    - No framework dependencies in domain/application
    - Proper use of annotations per layer
    - Fail-fast behavior (no auto-fix here)
    """

    def __init__(self, contracts_path: str | Path = "config/layer_contracts.yaml"):
        self.contracts_path = Path(contracts_path)

        if self.contracts_path.exists():
            self.contracts = yaml.safe_load(
                self.contracts_path.read_text(encoding="utf-8")
            ) or {}
        else:
            # Fallback: strong default rules (domain protected)
            self.contracts = {
                "layers": {
                    "domain": {
                        "forbidden_imports": [
                            "jakarta.*",
                            "javax.*",
                            "org.springframework.*",
                            "org.hibernate.*",
                        ],
                        "forbidden_annotations": [
                            "@Entity",
                            "@Table",
                            "@Column",
                            "@Id",
                            "@GeneratedValue",
                            "@Repository",
                            "@Service",
                            "@Component",
                            "@Autowired",
                            "@Transactional",
                            "@NotNull",
                            "@NotBlank",
                            "@NotEmpty",
                            "@Size",
                            "@Valid",
                        ],
                    }
                }
            }

        self.layers = self.contracts.get("layers", {})

    # -------------------------
    # Factory loader (used by main.py)
    # -------------------------
    @classmethod
    def load(
        cls, contracts_path: str | Path = "config/layer_contracts.yaml"
    ) -> "LayerContracts":
        return cls(contracts_path=contracts_path)

    # -------------------------
    # Layer resolution
    # -------------------------
    def layer_for_path(self, file_path: str | Path) -> Optional[str]:
        p = str(file_path).replace("\\", "/").lower()

        # ✅ tests first
        if "/src/test/java/" in p or p.startswith("backend/src/test/java/"):
            return "test"

        if "/domain/" in p:
            return "domain"
        if "/application/" in p:
            return "application"
        if "/adapters/" in p or "/interfaces/" in p:
            return "adapters"
        if "/infrastructure/" in p or "/infra/" in p:
            return "infrastructure"

        return None

    # -------------------------
    # Java source inspection
    # -------------------------
    def _extract_imports(self, java_source: str) -> List[str]:
        return re.findall(
            r"^\s*import\s+([^;]+);",
            java_source,
            flags=re.MULTILINE,
        )

    def _extract_annotations(self, java_source: str) -> List[str]:
        return re.findall(
            r"^\s*(@\w+)",
            java_source,
            flags=re.MULTILINE,
        )

    # -------------------------
    # Validation
    # -------------------------
    def validate(
        self, file_path: str | Path, java_source: str
    ) -> List[ContractViolation]:
        layer = self.layer_for_path(file_path)
        if not layer:
            return []

        rules = self.layers.get(layer, {})
        forbidden_imports = rules.get("forbidden_imports", [])
        forbidden_annotations = rules.get("forbidden_annotations", [])

        imports = self._extract_imports(java_source)
        annotations = self._extract_annotations(java_source)

        violations: List[ContractViolation] = []

        for imp in imports:
            for pattern in forbidden_imports:
                if fnmatch.fnmatch(imp, pattern):
                    violations.append(
                        ContractViolation(
                            rule=f"{layer}.forbidden_imports",
                            detail=f"Import '{imp}' forbidden by pattern '{pattern}'",
                        )
                    )

        for ann in annotations:
            if ann in forbidden_annotations:
                violations.append(
                    ContractViolation(
                        rule=f"{layer}.forbidden_annotations",
                        detail=f"Annotation '{ann}' forbidden in layer '{layer}'",
                    )
                )

        return violations

    # -------------------------
    # Fail-fast enforcement
    # -------------------------
    def validate_or_raise(self, file_path: str | Path, java_source: str) -> None:
        violations = self.validate(file_path, java_source)
        if not violations:
            return

        message = "\n".join(
            f"- [{v.rule}] {v.detail}" for v in violations
        )

        raise ValueError(
            f"Layer contract violated for '{file_path}':\n{message}"
        )