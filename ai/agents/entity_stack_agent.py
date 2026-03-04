"""
Entity Stack Agent

Generates the full stack of files for a domain entity.
"""

from concurrent.futures import ThreadPoolExecutor, as_completed


class EntityStackAgent:

    def __init__(self, executor, factory, max_workers: int = 6, logger=None):
        self.executor = executor
        self.factory = factory
        self.max_workers = max_workers
        self.logger = logger

    def generate(self, architecture: dict):
        """
        Generate stacks for all entities in parallel.
        """

        inventory = architecture.get("file_inventory", [])

        entities = {}

        # group files by entity
        for item in inventory:
            entity = item.get("entity")

            # skip entries that do not belong to an entity (e.g. enums/global files)
            if not entity:
                continue

            entities.setdefault(entity, []).append(item)

        with ThreadPoolExecutor(max_workers=self.max_workers) as pool:

            futures = {
                pool.submit(self.generate_entity_stack, entity, files): entity
                for entity, files in entities.items()
            }

            for future in as_completed(futures):
                entity = futures[future]

                try:
                    future.result()
                except Exception as e:
                    raise RuntimeError(
                        f"Entity stack generation failed for '{entity}': {e}"
                    ) from e

    def generate_entity_stack(self, entity, files):

        if self.logger:
            self.logger.info(f"⚙️ EntityStackAgent generating stack for {entity}")
        else:
            print(f"⚙️ EntityStackAgent generating stack for {entity}")

        for item in files:

            rel_path = item["path"]

            code = self.executor.run_task(
                "write_code",
                path=rel_path,
                desc=item.get("description"),
                context_data={
                    "entity": entity,
                    "path": rel_path,
                    "item": item,
                },
            )

            self.factory.save_to_disk(rel_path, code)