from ai.agents.base import AgentResult
from ai.pipeline.task_executor import TaskExecutor

class ArchitectureAgent:
    name = "architecture_agent"

    def __init__(self):
        self.executor = TaskExecutor()

    def run(self, ctx):
        domain_model = ctx["domain_agent.result"]
        raw = self.executor.run_task(
            "architecture_task",
            domain_model=domain_model,
            base_package=ctx["base_package"],
        )
        # Este raw debería incluir file_inventory o arquitectura
        return AgentResult(ok=True, artifact=raw if isinstance(raw, dict) else {"architecture_raw": raw})