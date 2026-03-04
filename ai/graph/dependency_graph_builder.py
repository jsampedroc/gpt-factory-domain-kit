from collections import defaultdict, deque


class DependencyGraphBuilder:

    def build(self, architecture):

        inventory = architecture.get("file_inventory", [])

        nodes = []
        edges = defaultdict(set)

        # collect nodes first
        for item in inventory:
            nodes.append(item["path"])

        # map entity → paths to make dependency resolution easier
        entity_paths = {}
        for item in inventory:
            entity = item.get("entity")
            if entity:
                entity_paths.setdefault(entity, []).append(item["path"])

        for item in inventory:

            path = item["path"]
            entity = item.get("entity")
            desc = item.get("description", "")

            if not entity:
                continue

            # Service depends on Repository + Entity
            if desc == "Service":
                dep = f"domain/repository/{entity}Repository.java"
                if dep in nodes:
                    edges[path].add(dep)

                dep = f"domain/model/{entity}.java"
                if dep in nodes:
                    edges[path].add(dep)

            # Repository depends on Entity
            if desc == "Repository Interface":
                dep = f"domain/model/{entity}.java"
                if dep in nodes:
                    edges[path].add(dep)

            # Controller depends on Service
            if desc == "Controller":
                dep = f"application/service/{entity}Service.java"
                if dep in nodes:
                    edges[path].add(dep)

            # Mapper depends on Entity
            if desc == "Mapper":
                dep = f"domain/model/{entity}.java"
                if dep in nodes:
                    edges[path].add(dep)

        return nodes, edges

    def topological_sort(self, nodes, edges):

        in_degree = {n: 0 for n in nodes}

        for n, deps in edges.items():
            for dep in deps:
                if dep in in_degree:
                    in_degree[n] += 1

        queue = deque([n for n in nodes if in_degree[n] == 0])

        ordered = []

        while queue:

            node = queue.popleft()
            ordered.append(node)

            for other in edges:
                if node in edges[other]:
                    in_degree[other] -= 1

                    if in_degree[other] == 0:
                        queue.append(other)

        return ordered

    def order_inventory(self, architecture):

        inventory = architecture.get("file_inventory", [])
        nodes, edges = self.build(architecture)
        ordered_paths = self.topological_sort(nodes, edges)

        by_path = {item["path"]: item for item in inventory}

        ordered_inventory = []
        for p in ordered_paths:
            if p in by_path:
                ordered_inventory.append(by_path[p])

        return ordered_inventory