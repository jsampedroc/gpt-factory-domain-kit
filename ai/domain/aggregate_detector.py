class AggregateDetector:

    """
    Detects Aggregate Roots and their members using structural heuristics
    only (no domain keywords).

    Heuristics:
    1. If an entity owns collections (List<OtherEntity>) it is likely the
       aggregate root and the referenced entities are members.
    2. If multiple aggregates are detected they remain independent.
    3. If no aggregates are detected a deterministic fallback selects the
       entity with the most fields.
    """

    def _extract_list_type(self, field_type: str):
        """
        Extracts entity name from List<EntityName>.
        """
        if not isinstance(field_type, str):
            return None

        if field_type.startswith("List<") and field_type.endswith(">"):
            return field_type[5:-1]

        return None

    def detect(self, domain_model):

        dm = domain_model.get("domain_model", domain_model)
        entities = dm.get("entities", [])

        aggregates = []

        entity_map = {e.get("name"): e for e in entities}

        for entity in entities:

            root_name = entity.get("name")
            fields = entity.get("fields", [])

            members = []

            for f in fields:

                member = self._extract_list_type(f.get("type"))

                if member and member in entity_map:
                    members.append(member)

            if members:
                aggregates.append({
                    "aggregate": root_name,
                    "entities": [root_name] + members,
                    "reason": "collection_ownership"
                })

        # deterministic fallback if nothing detected
        if not aggregates and entities:

            sorted_entities = sorted(
                entities,
                key=lambda x: len(x.get("fields", [])),
                reverse=True
            )

            root = sorted_entities[0]

            aggregates.append({
                "aggregate": root.get("name"),
                "entities": [root.get("name")],
                "reason": "fallback_largest_entity"
            })

        dm["aggregates"] = aggregates

        return domain_model