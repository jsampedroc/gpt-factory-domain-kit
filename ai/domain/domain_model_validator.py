def validate_domain_model(model: dict):

    dm = model.get("domain_model", model)

    errors = []

    # ---------------- ENTITIES ----------------
    for ent in dm.get("entities", []):
        name = ent.get("name")

        if not name:
            errors.append("Entity without name")

        fields = ent.get("fields", [])
        if not fields:
            errors.append(f"Entity '{name}' has no fields")

        for f in fields:
            if not f.get("name"):
                errors.append(f"Entity '{name}' has field without name")

            if not f.get("type"):
                errors.append(f"Entity '{name}' field '{f}' missing type")

    # ---------------- VALUE OBJECTS ----------------
    for vo in dm.get("value_objects", []):
        name = vo.get("name")

        if not name:
            errors.append("ValueObject without name")

        fields = vo.get("fields", [])
        if not fields:
            errors.append(f"ValueObject '{name}' has no fields")

    # ---------------- ENUMS ----------------
    for enum in dm.get("global_enums", []):
        name = enum.get("name")
        values = enum.get("values", [])

        if not name:
            errors.append("Enum without name")

        if not values:
            errors.append(f"Enum '{name}' has no values")

    if errors:
        raise RuntimeError(
            "Invalid domain model:\n" + "\n".join(errors)
        )