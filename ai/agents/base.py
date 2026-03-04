from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, Protocol


@dataclass
class AgentResult:
    ok: bool
    artifact: Dict[str, Any]
    notes: str = ""


class Agent(Protocol):
    name: str

    def run(self, ctx: Dict[str, Any]) -> AgentResult:
        ...