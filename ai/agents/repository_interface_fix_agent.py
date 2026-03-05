# ------------------ Repository Interface Fix Agent ------------------
class RepositoryInterfaceFixAgent:
    """
    Fixes missing semicolons in Java repository interfaces such as:
    Optional<Entity> findById(Id id)
    -> Optional<Entity> findById(Id id);
    """

    METHOD_RE = re.compile(r"^\s*(Optional<[^>]+>|List<[^>]+>|[A-Z][A-Za-z0-9_<>]*)\s+[a-zA-Z0-9_]+\([^)]*\)\s*$")

    def run(self, factory):

        repo_root = factory.output_root / "backend/src/main/java" / factory.base_package_path / "domain/repository"

        if not repo_root.exists():
            return

        for path in repo_root.rglob("*.java"):

            try:
                lines = path.read_text(encoding="utf-8").splitlines()
            except Exception:
                continue

            changed = False

            for i, line in enumerate(lines):
                if self.METHOD_RE.match(line) and not line.strip().endswith(";"):
                    lines[i] = line.rstrip() + ";"
                    changed = True

            if changed:
                try:
                    path.write_text("\n".join(lines), encoding="utf-8")
                    factory.log(f"🔧 Repository interface fix applied: {path.name}")
                except Exception:
                    pass