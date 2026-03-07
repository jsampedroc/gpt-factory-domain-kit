def build_code_generation_task(path, context_data=None, **kwargs):
    description = kwargs.get('description') or kwargs.get('desc') or "Generate backend logic code."
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
   - Import enums from the domain layer under '{base_package}.domain'.
   - The exact package (shared, enums, valueobject, etc.) must match the project structure inferred from the path.

3. FLAT HEXAGONAL ARCHITECTURE:
   - Domain entities → '{base_package}.domain.*'
   - Value object IDs → '{base_package}.domain.*'
   - Domain repositories → '{base_package}.domain.*'
   - Infrastructure persistence → '{base_package}.infrastructure.persistence.*'
   - Adapters → '{base_package}.infrastructure.*'

4. DTO NAMING:
   - Use suffix 'Request' or 'Response'

5. DTO ISOLATION RULES (CRITICAL):

- DTOs MUST NOT reference domain entities.
- DTO fields MUST use ONLY:
    - Java primitives (int, long, boolean, etc.)
    - Standard Java types (String, UUID, LocalDate, Instant, etc.)
    - Collections of primitives (List<String>, List<UUID>, etc.)
    - Other DTOs (ChildRequest, ChildResponse, etc.)

- NEVER use domain entities inside DTOs.

INVALID EXAMPLE:
    List<Child>

VALID EXAMPLES:
    List<UUID>
    List<ChildRequest>

DTO GENERATION RULES:

If the file being generated ends with:
- Request
- Response

then the class MUST be a plain DTO:

- private final fields
- full constructor
- value-style getters (fieldName())
- NO domain entity imports
- NO JPA annotations
- NO business logic

ENTITY RULES:

- Domain entities are **plain Java classes**
- NO annotations
- NO Lombok
- Must extend:

    Example (generic):

        public class <EntityName> extends Entity<<EntityName>Id>

CONSTRUCTOR RULES:

- Constructor MUST contain:
  id + all fields from the JSON context.

Example (generic):

    public <EntityName>(
        <EntityName>Id id,
        String firstField,
        String secondField
    )

SOURCE OF TRUTH (JSON MODEL):

{ctx}

The JSON above defines the exact structure of the domain model.
Fields defined in "fields" MUST appear in the generated class.

If fields are missing, the generated code is INVALID.
""",
        "expected_output": "Strict, complete, compilable Java 17 code."
    }