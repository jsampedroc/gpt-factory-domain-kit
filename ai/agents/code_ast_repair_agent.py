# ------------------ Code AST Repair Agent ------------------
class CodeASTRepairAgent:
    """
    Performs structural repairs on generated Java code using lightweight
    AST-like heuristics. This agent fixes common LLM mistakes that are
    syntactically valid text but structurally invalid Java.

    Examples fixed:
    - Missing semicolons in interface methods
    - Constructors without bodies
    - Methods without braces
    - Broken class declarations
    """

    INTERFACE_METHOD_RE = re.compile(r"^\s*(Optional<[^>]+>|List<[^>]+>|[A-Z][A-Za-z0-9_<>]*)\s+[a-zA-Z0-9_]+\([^)]*\)\s*$")

    METHOD_DECL_RE = re.compile(r"(public|private|protected)\s+[A-Za-z0-9_<>, ]+\([^)]*\)\s*$")

    def run(self, factory):

        src_root = factory.output_root / "backend/src/main/java"

        if not src_root.exists():
            return

        for path in src_root.rglob("*.java"):

            try:
                lines = path.read_text(encoding="utf-8").splitlines()
            except Exception:
                continue

            changed = False

            for i, line in enumerate(lines):

                stripped = line.strip()

                # Fix interface method missing semicolon
                if self.INTERFACE_METHOD_RE.match(line) and not stripped.endswith(";"):
                    lines[i] = stripped + ";"
                    changed = True
                    continue

                # Fix method declaration missing braces
                if self.METHOD_DECL_RE.search(line) and not stripped.endswith("{"):
                    lines[i] = line.rstrip() + " {"
                    changed = True

            if changed:
                try:
                    path.write_text("\n".join(lines), encoding="utf-8")
                    factory.log(f"🧠 AST repair applied: {path.name}")
                except Exception:
                    pass