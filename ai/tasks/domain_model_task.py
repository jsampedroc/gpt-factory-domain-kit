# ai/tasks/domain_model_task.py

def build_domain_model_task(idea, base_package, **kwargs):
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

  "valueObjects": [
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
  ]
}

IMPORTANT DOMAIN CONSTRAINT:

Do NOT invent concepts that are not present in the IDEA.

Forbidden examples unless explicitly mentioned in the IDEA:
Patient
Address
Money
Email
PhoneNumber
UserProfile
MedicalRecord

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

If a concept only represents a fixed set of values, it MUST be an enum.

3. ENUMS

Enums represent fixed sets of values.

Examples:
AllergySeverity
PaymentStatus
AttendanceType
ChildStatus

Example:

{
  "name": "AllergySeverity",
  "values": ["LOW","MEDIUM","HIGH","CRITICAL"]
}

TYPE SAFETY RULES

Field types MUST be one of:

- Java primitives
- String
- UUID
- LocalDate
- LocalDateTime
- an Entity defined in this model
- a ValueObject defined in this model
- an Enum defined in this model
- List<T> where T is a valid type above

INVALID TYPES (DO NOT GENERATE):

Address
Patient
Profile
Record
DataObject

OUTPUT RULES

1. Return ONLY the JSON object
2. NO markdown
3. NO explanations
4. Java 17 compatible types
""".replace("__IDEA__", idea)
    return {
        "agent": "domain_reasoner",
        "description": description,
        "expected_output": "Pure raw JSON DNA contract."
    }