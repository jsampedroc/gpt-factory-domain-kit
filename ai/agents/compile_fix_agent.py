from ai.agents.base import AgentResult
from ai.pipeline.task_executor import TaskExecutor

class CompileFixAgent:
    name = "compile_fix_agent"

    def __init__(self):
        self.executor = TaskExecutor()

    def run(self, ctx):
        # Expect compiler output in ctx
        compile_output = ctx.get("compile_output") or ctx.get("maven_output") or ""
        base_package = ctx.get("base_package", "")
        project_slug = ctx.get("project_slug", "")

        if not compile_output.strip():
            return AgentResult(ok=False, artifact={}, notes="No compile output provided")

        fixed = self.executor.run_task(
            "fix_compile_error",
            compile_output=compile_output,
            base_package=base_package,
            project_slug=project_slug,
        )

        return AgentResult(ok=True, artifact={"fix": fixed}, notes="Compile fix suggested")

AGENT_CLASS = CompileFixAgent
