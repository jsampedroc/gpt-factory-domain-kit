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

    def resolve(self, type_name, base_package, module=None):

        if not type_name:
            return None

        type_name = type_name.strip()

        # Normalize possible fully qualified types or generics
        simple_name = type_name.split(".")[-1]

        # Compute packages
        if module:
            model_pkg = f"{base_package}.{module}.domain.model"
        else:
            model_pkg = f"{base_package}.domain.model"

        # Value objects are module scoped when a module exists
        if module:
            vo_pkg = f"{base_package}.{module}.domain.valueobject"
        else:
            vo_pkg = f"{base_package}.domain.valueobject"

        # Shared types remain global
        shared_pkg = f"{base_package}.domain.shared"

        # Handle generic types like List<Child>
        if "<" in simple_name and ">" in simple_name:
            simple_name = simple_name.split("<", 1)[0].strip()

        # Ignore Java primitives
        if simple_name in {"int", "long", "double", "float", "boolean", "short", "byte", "char"}:
            return None

        if simple_name in self.JAVA_LANG:
            return None

        if simple_name in self.JAVA_STD:
            return self.JAVA_STD[simple_name]

        if simple_name.endswith("Id"):
            return f"{vo_pkg}.{simple_name}"

        if simple_name.endswith("Status") or simple_name.endswith("Type"):
            return f"{shared_pkg}.{simple_name}"

        if simple_name in self.value_objects:
            return f"{vo_pkg}.{simple_name}"

        # Do NOT automatically assume unknown types belong to domain.model.
        # This was causing wrong imports like:
        #   domain.model.List
        #   domain.model.LocalDate
        #   domain.model.AllergySeverity
        # The correct import will be resolved later using inventory/specs.

        return None