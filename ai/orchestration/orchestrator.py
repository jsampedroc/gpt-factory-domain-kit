from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, List

from ai.agents.base import Agent, AgentResult


@dataclass
class OrchestratorConfig:
    max_fix_rounds: int = 5


class Orchestrator:
    def __init__(self, agents: List[Agent], cfg: OrchestratorConfig):
        self.agents = agents
        self.cfg = cfg

    def run(self, initial_ctx: Dict[str, Any]) -> Dict[str, Any]:
        ctx = dict(initial_ctx)

        for agent in self.agents:
            res: AgentResult = agent.run(ctx)
            ctx[f"{agent.name}.result"] = res.artifact
            ctx[f"{agent.name}.notes"] = res.notes

            if not res.ok:
                raise RuntimeError(f"Agent failed: {agent.name}. {res.notes}")

            # Verify/Fix loop hook (if your pipeline separates verify/fix)
            if agent.name == "verify_agent" and res.artifact.get("status") != "green":
                ctx = self._fix_loop(ctx)

        return ctx

    def _fix_loop(self, ctx: Dict[str, Any]) -> Dict[str, Any]:
        for round_i in range(1, self.cfg.max_fix_rounds + 1):
            fix_agent = next(a for a in self.agents if a.name == "fix_agent")
            verify_agent = next(a for a in self.agents if a.name == "verify_agent")

            fix_res = fix_agent.run(ctx)
            ctx[f"fix_agent.round_{round_i}"] = fix_res.artifact

            verify_res = verify_agent.run(ctx)
            ctx[f"verify_agent.round_{round_i}"] = verify_res.artifact

            if verify_res.artifact.get("status") == "green":
                return ctx

        raise RuntimeError("Fix loop exhausted: project still failing verification")