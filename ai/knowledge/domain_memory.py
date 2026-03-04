import json
from pathlib import Path


class DomainMemory:

    def __init__(self, path="knowledge/domain_memory.json"):
        self.path = Path(path)

        if not self.path.exists():
            self.path.write_text(json.dumps({
                "aggregates": {},
                "value_objects": {},
                "events": {}
            }))

    def learn(self, signals):

        data = json.loads(self.path.read_text())

        for vo in signals.get("value_objects", []):
            data["value_objects"][vo] = data["value_objects"].get(vo, 0) + 1

        for agg, member in signals.get("aggregates", []):
            data["aggregates"][agg] = data["aggregates"].get(agg, 0) + 1

        self.path.write_text(json.dumps(data, indent=2))