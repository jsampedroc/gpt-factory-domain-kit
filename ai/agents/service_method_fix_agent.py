# ------------------ Service Method Fix Agent ------------------
class ServiceMethodFixAgent:
    """
    Ensures service methods missing braces are corrected.
    Example:
    public Course save(Course c)
    -> public Course save(Course c) {
    """

    METHOD_RE = re.compile(r"(public|private|protected)\s+[A-Za-z0-9_<>, ]+\([^)]*\)\s*$")

    def run(self, factory):

        svc_root = factory.output_root / "backend/src/main/java" / factory.base_package_path / "application/service"

        if not svc_root.exists():
            return

        for path in svc_root.rglob("*.java"):

            try:
                lines = path.read_text(encoding="utf-8").splitlines()
            except Exception:
                continue

            changed = False

            for i, line in enumerate(lines):
                if self.METHOD_RE.search(line) and "{" not in line:
                    lines[i] = line.rstrip() + " {"
                    changed = True

            if changed:
                try:
                    path.write_text("\n".join(lines), encoding="utf-8")
                    factory.log(f"🔧 Service method fix applied: {path.name}")
                except Exception:
                    pass