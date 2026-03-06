class JavaTypeResolver:

    """
    Resolves Java type imports deterministically to avoid LLM hallucinations.

    Rules:
    - java.lang types -> no import
    - known JDK types -> import from JDK
    - <Name>Id -> domain.valueobject
    - <Name>Status / <Name>Type -> domain.shared
    - discovered value objects -> domain.valueobject
    - everything else -> domain.model
    """

    JAVA_LANG = {
        "String", "Integer", "Long", "Boolean",
        "Double", "Float", "Short", "Byte",
        "Character"
    }

    JAVA_STD = {
        "LocalDate": "java.time.LocalDate",
        "LocalDateTime": "java.time.LocalDateTime",
        "Instant": "java.time.Instant",
        "UUID": "java.util.UUID",
        "List": "java.util.List",
        "Set": "java.util.Set",
        "Map": "java.util.Map",
        "Optional": "java.util.Optional",
        "BigDecimal": "java.math.BigDecimal",
    }

    def __init__(self, value_objects=None):
        self.value_objects = set(value_objects or [])

    def resolve(self, type_name, base_package):

        if not type_name:
            return None

        type_name = type_name.strip()

        # Remove generic wrappers like List<Child>
        if "<" in type_name and ">" in type_name:
            type_name = type_name.split("<", 1)[0].strip()

        # Ignore Java primitives
        if type_name in {"int", "long", "double", "float", "boolean", "short", "byte", "char"}:
            return None

        if type_name in self.JAVA_LANG:
            return None

        if type_name in self.JAVA_STD:
            return self.JAVA_STD[type_name]

        if type_name.endswith("Id"):
            return f"{base_package}.domain.valueobject.{type_name}"

        if type_name.endswith("Status") or type_name.endswith("Type"):
            return f"{base_package}.domain.shared.{type_name}"

        if type_name in self.value_objects:
            return f"{base_package}.domain.valueobject.{type_name}"

        return f"{base_package}.domain.model.{type_name}"