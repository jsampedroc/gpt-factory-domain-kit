"""ai.agents.domain_agent

This agent is invoked by main as:

    domain_model = DomainAgent().run(factory)

Where `factory` is an instance of SoftwareFactory.

It MUST NOT expect a dict-like ctx.
"""

import json


class DomainAgent:
    """Runs the LLM domain reasoning task and returns the raw domain model (dict)."""

    name = "domain"

    def __init__(self, factory=None):
        # Keep constructor flexible for AgentRegistry/_get
        self.factory = factory

    def run(self, factory):
        raw = factory.executor.run_task(
            "model_domain",
            idea=factory.idea,
            base_package=factory.base_package,
        )
        return json.loads(raw)
