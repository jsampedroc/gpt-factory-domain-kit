import subprocess


class TestRunnerAgent:

    def run(self, factory):

        factory.log("🧪 Running tests")

        backend = factory.output_root / "backend"

        result = subprocess.run(
            ["mvn", "-q", "test"],
            cwd=backend,
            capture_output=True,
            text=True
        )

        return result.returncode == 0