class LearningAgent:

    def run(self, factory):

        dm = factory.state.domain_model

        signals = {
            "entities": [e["name"] for e in dm.get("entities", [])],
            "value_objects": [v["name"] for v in dm.get("value_objects", [])],
        }

        if factory.domain_memory:
            factory.domain_memory.learn(signals)

        factory.log("🧠 LearningAgent updated domain memory")