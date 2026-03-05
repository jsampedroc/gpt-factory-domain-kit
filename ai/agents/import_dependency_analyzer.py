# ------------------ Import Dependency Analyzer ------------------

class ImportDependencyAnalyzer:
    """
    Reads generated Java files and detects dependencies based on `import` statements.
    This improves ordering for recompilation cycles (similar to Devin-style dependency graphs).
    """

    IMPORT_RE = re.compile(r"import\s+([a-zA-Z0-9_.]+);")

    def build_graph(self, factory, inventory):

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
                content = file_path.read_text(encoding="utf-8")
            except Exception:
                continue

            imports = self.IMPORT_RE.findall(content)

            for imp in imports:
                # convert import package to potential path
                rel = imp.replace(factory.base_package + ".", "")
                rel = rel.replace(".", "/") + ".java"

                for target in nodes:
                    if target.endswith(rel):
                        edges[path].add(target)

        return nodes, edges