class TestGenerationAgent:

    def run(self, factory):

        factory.log("🧪 Generating tests")

        factory.executor.run_task(
            "generate_tests",
            base_package=factory.base_package
        )