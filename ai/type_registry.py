class TypeRegistry:

    def __init__(self, inventory, patterns):
        self.types = {}

        for item in inventory:
            name = item["name"]
            desc = item["description"]
            self.types[name] = desc

        for vo in patterns.get("value_objects", []):
            self.types.setdefault(vo, "VALUEOBJECT")

        for agg in patterns.get("aggregates", []):
            self.types.setdefault(agg, "ENTITY")

        for enum in patterns.get("enums", []):
            self.types.setdefault(enum, "ENUM")

    def kind(self, name):
        return self.types.get(name)

    def is_enum(self, name):
        return self.kind(name) == "ENUM"

    def is_value_object(self, name):
        return self.kind(name) == "VALUEOBJECT"

    def is_entity(self, name):
        return self.kind(name) == "ENTITY"