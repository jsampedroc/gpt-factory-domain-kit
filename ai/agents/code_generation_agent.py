"""ai.agents.code_generation_agent

Parallel code generation.

main.py calls:
    CodeGenerationAgent().run(factory, inventory)

The factory already contains the hardened single-file generator:
    factory._generate_single_file(item, index, total)

So this agent just orchestrates parallel execution.
"""

from concurrent.futures import ThreadPoolExecutor, as_completed


class CodeGenerationAgent:
    name = "code_generation"

    def __init__(self, factory=None, max_workers: int | None = None):
        self.factory = factory
        self.max_workers = max_workers

    def run(self, factory, inventory: list[dict]) -> dict:
        total = len(inventory)
        if total == 0:
            factory.log("⚠️ CodeGenerationAgent: empty inventory")
            return {"generated_files": []}

        # Reasonable default: CPU-bound-ish due to IO/LLM calls.
        max_workers = self.max_workers or min(12, max(4, total // 10))

        generated = []
        failures = []

        def _job(i_item):
            i, item = i_item
            factory._generate_single_file(item, i, total)
            return item.get("path")

        with ThreadPoolExecutor(max_workers=max_workers) as ex:
            futures = {ex.submit(_job, (i, it)): it for i, it in enumerate(inventory, 1)}
            for fut in as_completed(futures):
                item = futures[fut]
                try:
                    p = fut.result()
                    if p:
                        generated.append(p)
                except Exception as e:
                    failures.append({"path": item.get("path"), "error": str(e)})
                    factory.log(f"❌ Code generation failed for {item.get('path')}: {e}")

        if failures:
            factory.log(f"⚠️ CodeGenerationAgent completed with {len(failures)} failures")
        else:
            factory.log("✅ CodeGenerationAgent completed")

        return {"generated_files": generated, "failures": failures}
