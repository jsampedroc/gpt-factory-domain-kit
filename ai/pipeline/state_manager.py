# ai/pipeline/state_manager.py
import json
from pathlib import Path


class StateManager:
    """
    Handles persistence of the factory pipeline state.

    Backwards compatible with the previous format but also supports
    new multi-agent artifacts such as planner results, verify reports, etc.
    """

    @staticmethod
    def save_specs(file_path, domain_model, architecture=None, generated_files=None, artifacts=None):
        data = {
            "domain_model": domain_model,
            "architecture": architecture,
            "generated_files": generated_files or [],
            "artifacts": artifacts or {}  # new multi-agent artifact storage
        }

        Path(file_path).parent.mkdir(parents=True, exist_ok=True)

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

    @staticmethod
    def load_specs(file_path, state):
        path = Path(file_path)
        if not path.exists():
            return False

        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Core pipeline state
        state.domain_model = data.get("domain_model")
        state.architecture = data.get("architecture")

        # Generated files (resume support)
        state.generated_files = data.get("generated_files", [])

        # Multi-agent artifacts (planner, verify, etc.)
        state.artifacts = data.get("artifacts", {})

        return True

    @staticmethod
    def update_artifact(file_path, key, value):
        """
        Incrementally update a single artifact without rewriting the whole pipeline manually.
        """
        path = Path(file_path)

        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        else:
            data = {
                "domain_model": None,
                "architecture": None,
                "generated_files": [],
                "artifacts": {}
            }

        artifacts = data.setdefault("artifacts", {})
        artifacts[key] = value

        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)