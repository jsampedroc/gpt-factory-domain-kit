# ai/tasks/code_generation_task.py

def build_code_generation_task(path, context_data=None, **kwargs):
    description = kwargs.get('description') or kwargs.get('desc') or "Generate domain-driven logic."
    ctx = context_data or ""
    base_package = kwargs.get('base_package', 'com.application')

    return {
        "agent": "backend_builder",
        "description": f"""
TASK: Implement Java 17 code for the file: '{path}'

OBJECTIVE:
{description}

STRICT GAMA ELITE RULES:

1. SPRING BOOT 3:
   - Use 'jakarta.*' packages (e.g., jakarta.validation.constraints.*)
   - NEVER use 'javax'.

2. ENUMS:
   - Import all enums from '{base_package}.domain.shared'.

3. FLAT HEXAGONAL ARCHITECTURE:
   - Domain entities → '{base_package}.domain.model'
   - Value object IDs → '{base_package}.domain.valueobject'
   - Domain repositories → '{base_package}.domain.repository'
   - JPA entities → '{base_package}.infrastructure.persistence.entity'
   - Adapters → '{base_package}.infrastructure.persistence.adapter'

4. DTO NAMING:
   - Use suffix 'Request' or 'Response'

CRITICAL DOMAIN RULES (NON-NEGOTIABLE):

1. If the JSON context contains a "fields" array, the class MUST declare ALL fields.
2. Each field MUST:
   - be declared as `private final`
   - appear in the constructor
   - expose a value-style getter (example: `fieldName()`).

3. DO NOT invent fields.
4. DO NOT omit fields.
5. If "fields" exist and they are not implemented, the output is INVALID.

ENTITY RULES:

- Domain entities are **plain Java classes**
- NO annotations
- NO Lombok
- Must extend:

    Entity<IdType>

Example:

    public class Child extends Entity<ChildId>

CONSTRUCTOR RULES:

- Constructor MUST contain:
  id + all fields from the JSON context.

Example:

    public Child(
        ChildId id,
        String firstName,
        String lastName
    )

SOURCE OF TRUTH (JSON MODEL):

{ctx}

The JSON above defines the exact structure of the domain model.
Fields defined in "fields" MUST appear in the generated class.

If fields are missing, the generated code is INVALID.
""",
        "expected_output": "Strict, complete, compilable Java 17 code."
    }