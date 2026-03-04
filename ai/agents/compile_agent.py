import subprocess


class CompileAgent:

    def __init__(self, project_root, logger=None):
        self.project_root = project_root
        self.logger = logger

    def compile(self):

        if self.logger:
            self.logger.info("🔨 CompileAgent running Maven build")

        result = subprocess.run(
            ["mvn", "clean", "compile"],
            cwd=self.project_root,
            capture_output=True,
            text=True
        )

        success = result.returncode == 0

        return {
            "success": success,
            "stdout": result.stdout,
            "stderr": result.stderr
        }