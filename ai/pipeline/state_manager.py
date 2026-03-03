# ai/pipeline/state_manager.py
import json
from pathlib import Path

class StateManager:
    @staticmethod
    def save_specs(file_path, domain_model, architecture=None, generated_files=None):
        data = {
            "domain_model": domain_model,
            "architecture": architecture,
            "generated_files": generated_files or [] # Lista de paths completados
        }
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

    @staticmethod
    def load_specs(file_path, state):
        if not Path(file_path).exists():
            return False
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            state.domain_model = data.get("domain_model")
            state.architecture = data.get("architecture")
            # Cargamos la lista de lo que ya se fabricó
            state.generated_files = data.get("generated_files", [])
        return True