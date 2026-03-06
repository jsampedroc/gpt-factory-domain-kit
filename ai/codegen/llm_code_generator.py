class LLMCodeGenerator:

    def __init__(self, executor):
        self.executor = executor

    def generate(self, rel_path, prompt, base_package, context_payload):

        code = self.executor.run_task(
            "write_code",
            path=rel_path,
            desc=prompt,
            base_package=base_package,
            context_data=context_payload
        )

        return code