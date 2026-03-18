def build_usecase_body_task(context_data=None, **kwargs):
    """
    Generates only the execute() method body for a use case class.
    Returns raw Java statements (no class wrapper, no method signature).
    """
    entity = kwargs.get("entity", "Entity")
    uc_name = kwargs.get("uc_name", entity)
    uc_type = kwargs.get("uc_type", "command")
    uc_description = kwargs.get("uc_description", "")
    uc_inputs = kwargs.get("uc_inputs", [])
    uc_returns = kwargs.get("uc_returns", entity)
    entity_fields = kwargs.get("entity_fields", [])

    dto_suffix = "Command" if uc_type == "command" else "Query"
    dto_var = dto_suffix.lower()

    # Build record accessor list: Java records use fieldName() NOT getFieldName()
    input_accessors = "\n".join(
        f"  - {inp.get('name')}: {inp.get('type')} → access via {dto_var}.{inp.get('name')}()"
        for inp in uc_inputs if inp.get("name")
    ) if uc_inputs else "  (no inputs)"

    # Build entity constructor signature to avoid arity mismatch
    # Non-id fields in entity definition
    non_id_fields = [
        f for f in entity_fields
        if f.get("name") and f.get("name") != "id"
    ]
    constructor_args = ", ".join(
        f"{f.get('type')} {f.get('name')}"
        for f in non_id_fields
    )
    full_constructor = f"{entity}Id id, {constructor_args}" if constructor_args else f"{entity}Id id"

    is_query = uc_type == "query"
    is_list = str(uc_returns).startswith("List")
    is_deactivate = "deactivat" in uc_name.lower() or "cancel" in uc_name.lower()

    entity_var = entity[0].lower() + entity[1:]

    if is_list:
        guidance = "return repository.findAll();"
    elif is_query:
        # findById using the id from the query input
        id_input = next((i for i in uc_inputs if "id" in i.get("name", "").lower()), None)
        if id_input:
            id_field = id_input["name"]
            guidance = (
                f"return repository.findById({dto_var}.{id_field}());"
            )
        else:
            guidance = "return repository.findAll().stream().findFirst();"
    elif is_deactivate:
        # Find-then-return pattern; avoid hallucinating domain methods
        id_input = next((i for i in uc_inputs if "id" in i.get("name", "").lower()), None)
        if id_input:
            id_field = id_input["name"]
            guidance = (
                f"return repository.findById({dto_var}.{id_field}())\n"
                f"    .orElseThrow(() -> new IllegalArgumentException(\"Not found: \" + {dto_var}.{id_field}()));"
            )
        else:
            guidance = "throw new UnsupportedOperationException(\"Not implemented\");"
    else:
        # Create/update command — construct the entity with all required args
        # Build constructor call using command inputs + UUID.randomUUID() for any missing id fields
        args_parts = ["new " + entity + "Id(UUID.randomUUID())"]
        for f in non_id_fields:
            fname = f.get("name")
            ftype = f.get("type", "")
            # check if this field is in the command inputs
            matching = next((i for i in uc_inputs if i.get("name") == fname), None)
            if matching:
                args_parts.append(f"{dto_var}.{fname}()")
            elif ftype.endswith("Id") or fname.endswith("Id"):
                args_parts.append("null")  # FK id — not in command
            else:
                args_parts.append("null")
        constructor_call = ",\n            ".join(args_parts)
        guidance = (
            f"{entity} {entity_var} = new {entity}(\n"
            f"            {constructor_call}\n"
            f"        );\n"
            f"        return repository.save({entity_var});"
        )

    description = f"""
TASK: Generate the body of the execute({entity[0].lower()}{entity[1:] if False else uc_name}{dto_suffix} {dto_var}) method for a use case class.

USE CASE: {uc_name}UseCase
TYPE: {uc_type}
DESCRIPTION: {uc_description or f"Implements {uc_name}"}

ENTITY: {entity}
ENTITY CONSTRUCTOR SIGNATURE (EXACT):
  {entity}({full_constructor})

{dto_suffix} RECORD INPUT ACCESSORS:
{input_accessors}

REPOSITORY METHODS:
  - {entity} save({entity} entity)
  - Optional<{entity}> findById(UUID id)
  - List<{entity}> findAll()

CRITICAL RULES:
1. Output ONLY raw Java statements inside execute() — no class, no method signature, no imports.
2. CRITICAL: {dto_suffix} IS A JAVA RECORD. Use {dto_var}.fieldName() — NOT {dto_var}.getFieldName().
3. Use ONLY the repository methods listed above. NO other methods.
4. NEVER call domain-specific methods like .deactivate(), .cancel(), .update() — they do not exist.
5. NEVER use EntityNotFoundException or any class not in java.util.* or java.time.*.
6. Use IllegalArgumentException for not-found cases.
7. Match the entity constructor EXACTLY — use null for fields not available from the {dto_suffix}.
8. Keep the body under 10 lines.

SUGGESTED IMPLEMENTATION:
{guidance}

Output the suggested implementation above, adjusted for the exact accessor syntax.
"""

    return {
        "agent": "backend_builder",
        "description": description,
        "expected_output": "Raw Java statements for execute() body only."
    }
