class FileGenerationOrder:

    """
    Deterministic ordering of generated files to guarantee
    that dependencies are generated before they are referenced.
    """

    ORDER = {
        "VALUE_OBJECT": 1,
        "ENTITY_ID": 2,
        "ENTITY": 3,
        "REPOSITORY": 4,
        "SERVICE": 5,
        "CONTROLLER": 6,
        "DTO": 7,
        "MAPPER": 8,
        "JPA_ENTITY": 9,
        "SPRING_REPOSITORY": 10,
        "ADAPTER": 11,
    }

    @classmethod
    def detect_type(cls, path: str):

        if "valueobject" in path:
            return "VALUE_OBJECT"

        if path.endswith("Id.java"):
            return "ENTITY_ID"

        if "domain/model" in path:
            return "ENTITY"

        if "repository" in path and "domain" in path:
            return "REPOSITORY"

        if "service" in path:
            return "SERVICE"

        if "controller" in path or "rest" in path:
            return "CONTROLLER"

        if "dto" in path:
            return "DTO"

        if "mapper" in path:
            return "MAPPER"

        if "JpaEntity" in path:
            return "JPA_ENTITY"

        if "SpringData" in path:
            return "SPRING_REPOSITORY"

        if "adapter" in path:
            return "ADAPTER"

        return "ZZZ"

    @classmethod
    def sort_inventory(cls, inventory):

        def order(item):

            path = item.get("path", "")
            t = cls.detect_type(path)

            return cls.ORDER.get(t, 999)

        return sorted(inventory, key=order)