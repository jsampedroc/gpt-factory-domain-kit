"""ai.agents.compile_agent

main.py expects:
    success, output = CompileAgent().run(factory)

We delegate to SoftwareFactory._compile_project() when available.
"""

from pathlib import Path


class CompileAgent:
    name = "compile"

    def __init__(self, factory_or_root=None, logger=None):
        self.logger = logger
        self.factory = None
        self.project_root: Path | None = None

        if factory_or_root is None:
            return

        # Accept either factory or a path
        if hasattr(factory_or_root, "output_root") and hasattr(factory_or_root, "_compile_project"):
            self.factory = factory_or_root
        else:
            self.project_root = Path(factory_or_root)

    def run(self, factory):
        # Prefer factory internal compile helper
        if hasattr(factory, "_compile_project"):
            return factory._compile_project()

        # Fallback: attempt Maven compile under <root>/backend
        root = self.project_root or getattr(factory, "output_root", None)
        if root is None:
            return True, ""

        backend = Path(root) / "backend"
        if not backend.exists():
            return True, ""

        import subprocess

        result = subprocess.run(
            ["mvn", "-q", "-DskipTests", "package"],
            cwd=backend,
            capture_output=True,
            text=True,
        )

        out = (result.stdout or "") + "\n" + (result.stderr or "")
        return (result.returncode == 0), out
