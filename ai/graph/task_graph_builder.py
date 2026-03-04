class TaskGraphBuilder:

    def build(self, architecture):

        tasks = []

        entities = architecture.get("entities", [])

        for entity in entities:

            tasks.append({
                "type": "entity",
                "entity": entity["name"]
            })

            tasks.append({
                "type": "repository",
                "entity": entity["name"]
            })

            tasks.append({
                "type": "service",
                "entity": entity["name"]
            })

            tasks.append({
                "type": "controller",
                "entity": entity["name"]
            })

        return tasks