class RuntimeFeedbackAgent:
    """
    Analyzes runtime logs and execution results to detect issues
    after compilation and refactoring.
    """

    def run(self, factory):

        report = {
            "errors": [],
            "warnings": []
        }

        try:
            log_file = factory.output_root / "execution.log"

            if not log_file.exists():
                return report

            content = log_file.read_text()

            if "Exception" in content:
                report["errors"].append("runtime_exception")

            if "WARNING" in content:
                report["warnings"].append("runtime_warning")

        except Exception as e:
            factory.log(f"⚠️ Runtime feedback analysis error: {e}")

        return report