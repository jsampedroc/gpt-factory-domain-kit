import importlib
import pkgutil
from dataclasses import dataclass
from typing import Dict, Type, Any

@dataclass(frozen=True)
class LoadedAgent:
    name: str
    cls: Type[Any]
    module: str

class AgentRegistry:
    """Lightweight plugin loader for ai.agents.* modules."""

    @staticmethod
    def discover(package: str = "ai.agents") -> Dict[str, LoadedAgent]:
        pkg = importlib.import_module(package)
        out: Dict[str, LoadedAgent] = {}
        for m in pkgutil.iter_modules(pkg.__path__):  # type: ignore[attr-defined]
            if m.name.startswith("_"):
                continue
            modname = f"{package}.{m.name}"
            mod = importlib.import_module(modname)
            # Convention: module may expose AGENT_CLASS or a class with attribute 'name'
            cls = getattr(mod, "AGENT_CLASS", None)
            if cls is None:
                for v in mod.__dict__.values():
                    if isinstance(v, type) and getattr(v, "name", None):
                        cls = v
                        break
            if cls is None:
                continue
            out[getattr(cls, "name")] = LoadedAgent(name=getattr(cls, "name"), cls=cls, module=modname)
        return out
