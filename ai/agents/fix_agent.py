class FixAgent:

    def __init__(self, executor, logger=None):
        self.executor = executor
        self.logger = logger

    def fix(self, compile_result):

        errors = compile_result["stderr"]

        if self.logger:
            self.logger.info("🩹 FixAgent attempting automatic repair")

        fix = self.executor.run_task(
            "heal_code",
            errors=errors
        )

        return fix