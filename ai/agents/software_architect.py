"""DEPRECATED module kept for backwards compatibility.

This project migrated to the pipeline agents under ai.agents.* (e.g., domain_agent, code_generation_agent).
Avoid importing this module in new code.
"""

# No-op placeholder to avoid ModuleNotFoundError in older branches.
class DeprecatedAgent:
    name = "software_architect"

    def __init__(self, *a, **k):
        pass

    def run(self, *a, **k):
        return {"ok": False, "notes": "Deprecated agent stub: software_architect.py"}
