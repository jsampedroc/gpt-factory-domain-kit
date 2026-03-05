"""ai.agents.architecture_agent

main.py calls:

    architecture = ArchitectureAgent().run(factory, domain_model)

This agent returns a dict with at least:

    {"file_inventory": [...]} 

Inventory items must contain enough context for generation:
- path
- description
- entity
- fields/values when applicable

We leverage SoftwareFactory.generate_inventory() to ensure consistency.
"""


class ArchitectureAgent:
    name = "architecture"

    def __init__(self, factory=None):
        self.factory = factory

    def run(self, factory, domain_model: dict) -> dict:
        # Deterministic inventory generation (preferred) — avoids LLM hallucinations.
        inventory = factory.generate_inventory(domain_model)
        return {"file_inventory": inventory}
