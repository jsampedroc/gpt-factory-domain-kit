"""ai.agents.import_dependency_analyzer

Scans generated Java source files and builds a lightweight dependency graph
based on `import ...;` statements.

main.py uses:
    nodes, edges = ImportDependencyAnalyzer().build_graph(factory, inventory)
"""

import re
from collections import defaultdict


class ImportDependencyAnalyzer:
    """Detect dependencies between generated files using import statements."""

    IMPORT_RE = re.compile(r"import\s+([a-zA-Z0-9_.]+);")

    def build_graph(self, factory, inventory):
        nodes = [it.get("path") for it in inventory if it.get("path")]
        edges = defaultdict(set)

        for item in inventory:
            rel_path = item.get("path")
            if not rel_path:
                continue

            file_path = factory.resolve_output_path(rel_path)
            if not file_path.exists():
                continue

            try:
                content = file_path.read_text(encoding="utf-8")
            except Exception:
                continue

            for imp in self.IMPORT_RE.findall(content):
                # Convert import FQN to a relative path candidate
                if imp.startswith(factory.base_package + "."):
                    rel = imp[len(factory.base_package) + 1 :]
                else:
                    rel = imp

                rel = rel.replace(".", "/") + ".java"

                for target in nodes:
                    if target.endswith(rel):
                        edges[rel_path].add(target)

        return nodes, edges
