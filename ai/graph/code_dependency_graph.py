import re
from collections import defaultdict


class CodeDependencyGraph:

    IMPORT_RE = re.compile(r"import\s+([a-zA-Z0-9_.]+);")

    def build(self, factory, inventory):

        nodes = []
        edges = defaultdict(set)

        for item in inventory:
            nodes.append(item["path"])

        for item in inventory:

            path = item["path"]
            file_path = factory.resolve_output_path(path)

            if not file_path.exists():
                continue

            try:
                content = file_path.read_text()
            except Exception:
                continue

            imports = self.IMPORT_RE.findall(content)

            for imp in imports:

                rel = imp.replace(factory.base_package + ".", "")
                rel = rel.replace(".", "/") + ".java"

                for node in nodes:
                    if node.endswith(rel):
                        edges[path].add(node)

        return nodes, edges