import json
from ai.agents.base import AgentResult
from ai.pipeline.task_executor import TaskExecutor

class CodeGenerationAgent:
    """Compatibility wrapper around the original CodegenAgent pattern."""
    name = "code_generation_agent"

    def __init__(self, save_to_disk_fn=None):
        self.executor = TaskExecutor()
        self.save_to_disk = save_to_disk_fn

    def run(self, ctx):
        arch = ctx.get("architecture_agent.result") or ctx.get("architecture") or {}
        inventory = arch.get("file_inventory") or arch.get("architecture", {}).get("file_inventory")
        if not inventory:
            return AgentResult(ok=False, artifact={}, notes="No file_inventory found")

        generated = []
        for item in inventory:
            rel_path = item["path"]
            code = self.executor.run_task(
                "write_code",
                path=rel_path,
                desc=item.get("prompt") or item.get("desc", "") or "",
                base_package=ctx.get("base_package", ""),
                context_data=json.dumps(item),
            )
            if self.save_to_disk:
                self.save_to_disk(rel_path, code)
            generated.append(rel_path)

        return AgentResult(ok=True, artifact={"generated_files": generated}, notes="Code generated")

AGENT_CLASS = CodeGenerationAgent
