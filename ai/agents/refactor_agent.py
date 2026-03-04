class RefactorAgent:

    def run(self, factory):

        issues = []

        for java_file in factory.output_root.rglob("*.java"):

            try:
                code = java_file.read_text()
            except Exception:
                continue

            if len(code) > 2000:
                issues.append(java_file)

        if not issues:
            return

        factory.log(f"🧠 Refactor agent analyzing {len(issues)} files")