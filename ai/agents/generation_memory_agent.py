# ------------------ Generation Memory Agent ------------------
class GenerationMemoryAgent:
    """
    Stores recurring generation errors and successful fixes so the factory
    progressively improves over time (self‑improving software factory).
    """

    def __init__(self):
        from ai.knowledge.compile_error_memory import CompileErrorMemory
        self.memory = CompileErrorMemory()

    def record_failure(self, error_log):
        try:
            self.memory.record(error_log[:500], "compile_failure")
        except Exception:
            pass

    def record_success(self, context):
        try:
            self.memory.record("SUCCESS_PATTERN", context[:500])
        except Exception:
            pass