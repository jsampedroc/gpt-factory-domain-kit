import json
from pathlib import Path


class CompileMemory:

    FILE = Path("memory/compile_patterns.json")

    def __init__(self):
        self.FILE.parent.mkdir(exist_ok=True)

        if self.FILE.exists():
            self.patterns = json.loads(self.FILE.read_text())
        else:
            self.patterns = []

    def record(self, error, fix):

        entry = {
            "error": error,
            "fix": fix
        }

        self.patterns.append(entry)

        self.FILE.write_text(
            json.dumps(self.patterns, indent=2)
        )

    def get_patterns(self):
        return self.patterns