# ai/domain/domain_knowledge_cache.py

import json
from pathlib import Path

KNOWLEDGE_FILE = Path("knowledge/domain_patterns.json")


def load_knowledge():

    if not KNOWLEDGE_FILE.exists():
        return {
            "value_objects": [],
            "aggregates": [],
            "events": [],
            "patterns": []
        }

    return json.loads(KNOWLEDGE_FILE.read_text())


def save_knowledge(data):

    KNOWLEDGE_FILE.parent.mkdir(parents=True, exist_ok=True)

    KNOWLEDGE_FILE.write_text(
        json.dumps(data, indent=2)
    )


def update_knowledge(domain_model):

    knowledge = load_knowledge()

    for vo in domain_model.get("value_objects", []):
        name = vo.get("name")
        if name and name not in knowledge["value_objects"]:
            knowledge["value_objects"].append(name)

    for agg in domain_model.get("aggregates", []):
        root = agg.get("aggregate")
        if root and root not in knowledge["aggregates"]:
            knowledge["aggregates"].append(root)

    for ev in domain_model.get("domain_events", []):
        name = ev.get("event")
        if name and name not in knowledge["events"]:
            knowledge["events"].append(name)

    save_knowledge(knowledge)