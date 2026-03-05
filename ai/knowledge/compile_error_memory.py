import json
from pathlib import Path

class CompileErrorMemory:

    FILE = Path("knowledge/compile_errors.json")

    def __init__(self):
        self.FILE.parent.mkdir(exist_ok=True)

        if self.FILE.exists():
            self.data = json.loads(self.FILE.read_text())
        else:
            self.data = []

    def record(self, error, fix):
        self.data.append({
            "error": error,
            "fix": fix
        })
        self.FILE.write_text(json.dumps(self.data, indent=2))

    def suggest(self, error):
        for e in self.data:
            if e["error"] in error:
                return e["fix"]
        return None