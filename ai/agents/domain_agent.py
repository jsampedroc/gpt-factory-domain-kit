import json
from ai.agents.base import AgentResult
from ai.pipeline.task_executor import TaskExecutor
from ai.domain.semantic_type_detector import detect_semantic_types

class DomainAgent:
    name = "domain_agent"

    def __init__(self):
        self.executor = TaskExecutor()

    def run(self, ctx):
        raw = self.executor.run_task(
            "model_domain",
            idea=ctx["idea"],
            base_package=ctx["base_package"],
        )
        dm = json.loads(raw)
        dm = detect_semantic_types(dm)  # tu motor actual
        return AgentResult(ok=True, artifact=dm, notes="Domain model + semantic enrichment")