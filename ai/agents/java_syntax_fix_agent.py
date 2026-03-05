
# ------------------ Java Syntax Fix Agent ------------------
class JavaSyntaxFixAgent:
    """
    Performs lightweight syntax repairs on generated Java files before
    the compilation phase. Fixes common LLM mistakes such as missing
    braces after method declarations.
    """

    METHOD_DECL_RE = re.compile(r"(public|private|protected)\s+[^{;]+\)\s*$")

    def run(self, factory):

        root = factory.output_root / "backend/src/main/java"

        if not root.exists():
            return

        for path in root.rglob("*.java"):

            try:
                content = path.read_text(encoding="utf-8")
            except Exception:
                continue

            lines = content.splitlines()
            changed = False

            for i, line in enumerate(lines):
                if self.METHOD_DECL_RE.search(line):
                    if i + 1 < len(lines) and "{" not in lines[i]:
                        lines[i] = line + " {"
                        changed = True

            if changed:
                try:
                    path.write_text("\n".join(lines), encoding="utf-8")
                    factory.log(f"🔧 Syntax fix applied: {path.name}")
                except Exception:
                    pass