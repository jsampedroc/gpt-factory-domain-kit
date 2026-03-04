import json
from ai.agents.base import AgentResult
from ai.pipeline.task_executor import TaskExecutor

class PlannerAgent:
    name = "planner_agent"

    def __init__(self):
        self.executor = TaskExecutor()

    def run(self, ctx):
        raw = self.executor.run_task(
            "plan_project",
            idea=ctx["idea"],
            base_package=ctx["base_package"],
        )
        return AgentResult(ok=True, artifact=json.loads(raw), notes="Plan generated")