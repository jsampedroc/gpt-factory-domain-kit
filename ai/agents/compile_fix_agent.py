"""ai.agents.compile_fix_agent

main.py expects:
    result = CompileFixAgent().run(factory, compile_output)

This agent calls TaskExecutor task: "generate_systemic_fix" (mapped in your TaskExecutor)
and applies returned patches when possible.

Return value:
- dict with keys: fixed(bool), regenerate(list[str])
"""

import json
from pathlib import Path


class CompileFixAgent:
    name = "compile_fix"

    def __init__(self, factory=None):
        self.factory = factory

    def _apply_files(self, factory, files: list[dict]) -> None:
        for f in files:
            rel = (f.get("path") or "").lstrip("/")
            content = f.get("content")
            if not rel or content is None:
                continue

            # Allow updating pom.xml during repair
            if rel == "backend/pom.xml":
                factory.save_to_disk(rel, content, is_protected=True)
                continue

            # Normal generation outputs
            factory.save_to_disk(rel, content, is_protected=False)

    def run(self, factory, compile_output: str):
        if not (compile_output or "").strip():
            return {"fixed": False, "regenerate": []}

        # Ask the LLM for a systemic fix plan
        raw = factory.executor.run_task(
            "generate_systemic_fix",
            compile_output=compile_output,
            base_package=factory.base_package,
            project_slug=factory.project_slug,
        )

        # Best-effort parse. We support either:
        # 1) JSON dict with {files:[{path,content}], regenerate:[...]}
        # 2) JSON list of files
        # 3) Plain text (no-op)
        try:
            data = json.loads(raw)
        except Exception:
            # If the model didn't return JSON, we can't safely apply.
            factory.log("⚠️ CompileFixAgent: non-JSON fix response; skipping apply")
            return {"fixed": False, "regenerate": []}

        files = []
        regen = []

        if isinstance(data, dict):
            files = data.get("files") or data.get("patches") or []
            regen = data.get("regenerate") or []
        elif isinstance(data, list):
            files = data

        if isinstance(files, list) and files:
            try:
                self._apply_files(factory, files)
                factory.log(f"🧩 CompileFixAgent: applied {len(files)} file patch(es)")
            except Exception as e:
                factory.log(f"⚠️ CompileFixAgent: failed applying patches: {e}")
                return {"fixed": False, "regenerate": []}

        return {"fixed": True, "regenerate": regen if isinstance(regen, list) else []}
