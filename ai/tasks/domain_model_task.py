# ai/tasks/domain_model_task.py

import json
import os

def build_domain_model_task(idea, base_package, **kwargs):
    def _load_rules():
        default = {
            "enum_suffixes": ["Status", "Type", "Severity", "Level", "Role"],
            "forbidden_concepts": [],
            "min_entities": 3,
            "require_ids_for_relationships": True,
            "allow_entity_references": False,
            "require_non_empty_value_objects": True
        }
        try:
            root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            path = os.path.join(root, "config", "domain_rules.json")
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                default.update({k: data.get(k, v) for k, v in default.items()})
        except Exception:
            pass
        return default

    rules = _load_rules()
    forbidden_block = "\n".join(rules["forbidden_concepts"]) 
    enum_suffixes = ", ".join(rules["enum_suffixes"]) 
    min_entities = rules["min_entities"]

    description = """
TASK: Convert the following business idea into a STRICT TECHNICAL DOMAIN MODEL in JSON.

IDEA:
__IDEA__

OUTPUT FORMAT (STRICT JSON ONLY):

{
  "entities": [
    {
      "name": "ExampleEntity",
      "fields": [
        {"name": "name", "type": "String"},
        {"name": "createdAt", "type": "LocalDate"}
      ]
    }
  ],

  "value_objects": [
    {
      "name": "ExampleValueObject",
      "fields": [
        {"name": "value", "type": "String"}
      ]
    }
  ],

  "enums": [
    {
      "name": "ExampleStatus",
      "values": ["VALUE1","VALUE2"]
    }
  ],

  "modules": {
    "modulename": {
      "entities": ["ExampleEntity"],
      "use_cases": [
        {
          "name": "CreateExample",
          "type": "command",
          "description": "Creates a new ExampleEntity",
          "inputs": [{"name": "fieldName", "type": "String"}],
          "returns": "ExampleEntity"
        },
        {
          "name": "GetExampleById",
          "type": "query",
          "description": "Retrieves an ExampleEntity by its ID",
          "inputs": [{"name": "id", "type": "UUID"}],
          "returns": "ExampleEntity"
        }
      ]
    }
  }
}

IMPORTANT DOMAIN CONSTRAINT:

Do NOT invent concepts that are not present in the IDEA.

Forbidden examples unless explicitly mentioned in the IDEA:
__FORBIDDEN__

MODULE GENERATION RULES (CRITICAL)

EXTRACTION RULE (CRITICAL)

- You MUST extract ALL nouns / business concepts from the IDEA
- Each noun MUST become either an Entity, ValueObject or Enum
- If a noun represents a core business concept → it MUST be an Entity
- NEVER return only one entity if multiple concepts are present

- You MUST extract ALL relevant core concepts from the IDEA
- Each core concept MUST be represented as an Entity, ValueObject, or Enum
- DO NOT collapse the entire domain into a single concept
- DO NOT omit concepts explicitly mentioned in the IDEA

AGGREGATE / ENTITY SEPARATION RULES (CRITICAL)

- Each major business concept MUST be modeled as a separate Entity
- DO NOT merge unrelated concepts into a single Entity
- Concepts mentioned in the IDEA MUST NOT be embedded inside another entity

For example, if the IDEA contains:
"children, parents, allergies, immunizations, authorized pickups"

Then you MUST create SEPARATE entities:
- Child
- Parent
- Allergy
- Immunization
- AuthorizedPickup

INVALID (DO NOT DO THIS):

{
  "entities": [
    {
      "name": "Appointment",
      "fields": [
        {"name": "child", "type": "Child"},
        {"name": "allergies", "type": "List<Allergy>"}
      ]
    }
  ]
}

VALID (REQUIRED):

{
  "entities": [
    {"name": "Child", "fields": [...]},
    {"name": "Parent", "fields": [...]},
    {"name": "Allergy", "fields": [...]},
    {"name": "Immunization", "fields": [...]},
    {"name": "AuthorizedPickup", "fields": [...]}
  ]
}

Example:
Input:
"children, parents, allergies, immunizations, authorized pickups"

Output MUST include entities or types representing:
- Child
- Parent
- Allergy
- Immunization
- AuthorizedPickup


MINIMUM REQUIREMENTS

- At least __MIN_ENTITIES__ entities MUST be generated when multiple concepts exist
- Each entity MUST have at least 1 field
- The model MUST reflect ALL major concepts from the IDEA

- If the IDEA contains 5 or more distinct concepts → generate at least 5 entities


CRITICAL MODELING RULES

1. ENTITIES

Entities represent core domain objects.

Rules:
- Entities MUST have fields
- Entities MUST have at least 1 field
- Entity names MUST be singular

Example:
{
  "name": "Child",
  "fields": [
    {"name": "firstName", "type": "String"},
    {"name": "birthDate", "type": "LocalDate"}
  ]
}

2. VALUE OBJECTS

ValueObjects represent immutable structured concepts.

Rules:
- MUST contain fields
- MUST NOT be empty
- MUST NOT represent simple scalar values

VALID valueObject example:

{
  "name": "GeoLocation",
  "fields": [
    {"name": "latitude", "type": "Double"},
    {"name": "longitude", "type": "Double"}
  ]
}

INVALID valueObject examples:

{ "name": "GeoLocation" }
{ "name": "AllergySeverity" }

- Concepts like Allergy, Immunization, Treatment, Appointment MUST be Entities, NOT ValueObjects

If a concept only represents a fixed set of values, it MUST be an enum.

- If a ValueObject has no fields → DO NOT generate it
- If the concept is a label or classification → use Enum instead

3. ENUMS

Enums represent fixed sets of values.

Examples:
ExampleStatus
ExampleType
ExampleCategory
ExampleLevel

Example:

{
  "name": "AllergySeverity",
  "values": ["LOW","MEDIUM","HIGH","CRITICAL"]
}

- If a field name ends with: __ENUM_SUFFIXES__ → it MUST be an enum
- Enum values MUST be explicitly generated (not empty)

TYPE SAFETY RULES

Field types MUST be one of:

- Java primitives
- String
- UUID
- LocalDate
- LocalDateTime
- <EntityName>Id (UUID-based identifier for an entity)
- a ValueObject defined in this model
- an Enum defined in this model
- List<T> where T is a valid type above

RELATIONSHIP RULES (CRITICAL)

- Entities MUST NOT reference other Entities directly
- Relationships MUST be represented using IDs only

VALID:
{
  "name": "Appointment",
  "fields": [
    {"name": "patientId", "type": "UUID"},
    {"name": "dentistId", "type": "UUID"}
  ]
}

INVALID:
{
  "name": "Appointment",
  "fields": [
    {"name": "patient", "type": "Patient"}
  ]
}

- Collections of entities MUST use IDs:
- DO NOT collapse related concepts into a single aggregate

USE CASE RULES (CRITICAL)

For EVERY module you define, you MUST generate meaningful business use_cases.
DO NOT generate only CRUD (Create/Update/Delete/Get). Generate real business operations.

Rules:
- Each module MUST have at least 4 use_cases
- use_cases MUST reflect real business operations for the domain
- types: "command" (changes state) or "query" (reads state)
- "inputs" MUST match the fields needed for the operation
- "returns" MUST be the entity or list of entities returned

Example for a dental clinic appointment module:
{
  "name": "ScheduleAppointment",
  "type": "command",
  "description": "Schedules a new appointment between a patient and dentist",
  "inputs": [
    {"name": "patientId", "type": "UUID"},
    {"name": "dentistId", "type": "UUID"},
    {"name": "appointmentDate", "type": "LocalDateTime"}
  ],
  "returns": "Appointment"
},
{
  "name": "CancelAppointment",
  "type": "command",
  "description": "Cancels an existing appointment and updates its status",
  "inputs": [{"name": "appointmentId", "type": "UUID"}],
  "returns": "Appointment"
},
{
  "name": "GetPatientAppointments",
  "type": "query",
  "description": "Returns all appointments for a given patient",
  "inputs": [{"name": "patientId", "type": "UUID"}],
  "returns": "List<Appointment>"
}

MODULES RULE: Every entity MUST belong to exactly one module.
Every module MUST have at least one entity and at least 4 use_cases.

OUTPUT RULES

1. Return ONLY the JSON object
2. NO markdown
3. NO explanations
4. Java 17 compatible types
""".replace("__IDEA__", idea) \
   .replace("__FORBIDDEN__", forbidden_block) \
   .replace("__ENUM_SUFFIXES__", enum_suffixes) \
   .replace("__MIN_ENTITIES__", str(min_entities))
    return {
        "agent": "domain_reasoner",
        "description": description,
        "expected_output": "Pure raw JSON DNA contract."
    }