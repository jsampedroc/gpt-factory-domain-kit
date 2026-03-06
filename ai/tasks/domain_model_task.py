# ai/tasks/domain_model_task.py

def build_domain_model_task(idea, base_package, **kwargs):
    return {
        "agent": "domain_reasoner",
        "description": f"""
        TASK: Distill the following business idea into a TECHNICAL JSON DOMAIN MODEL.

        IDEA: '{idea}'

        REQUIRED STRUCTURE (STRICT JSON ONLY):
        {{
          "entities": [
            {{
              "name": "Patient",
              "fields": [
                {{"name": "firstName", "type": "String"}},
                {{"name": "birthDate", "type": "LocalDate"}}
              ]
            }}
          ],

          "valueObjects": [
            {{
              "name": "Address",
              "fields": [
                {{"name": "street", "type": "String"}},
                {{"name": "city", "type": "String"}}
              ]
            }}
          ],

          "enums": [
            {{
              "name": "AppointmentStatus",
              "values": ["SCHEDULED", "CONFIRMED", "CANCELLED"]
            }}
          ]
        }}

        CRITICAL MODELING RULES:

        1. ENTITIES represent core domain objects and MUST contain fields.

        2. VALUE OBJECTS represent structured immutable concepts and MUST contain fields.

        VALUE OBJECT RULES (STRICT):
        - Every valueObject MUST include a non-empty "fields" array.
        - A valueObject WITHOUT fields is INVALID.
        - If a concept has no internal structure (only a set of fixed values), it MUST be an enum instead.

        VALID valueObject example:
        {{
          "name": "Address",
          "fields": [
            {{"name": "street", "type": "String"}},
            {{"name": "city", "type": "String"}}
          ]
        }}

        INVALID valueObject examples (DO NOT GENERATE):
        {{ "name": "Address" }}
        {{ "name": "AllergySeverity" }}

        These would instead be modeled as:

        ENUM example:
        {{
          "name": "AllergySeverity",
          "values": ["LOW","MEDIUM","HIGH","CRITICAL"]
        }}

        3. ENUMS represent fixed sets of possible values such as:
           status, type, severity, level, role, category.

        Examples of enums:
        AllergySeverity
        PaymentStatus
        AttendanceType
        InvoiceStatus

        ENUM FORMAT:
        {{
          "name": "AllergySeverity",
          "values": ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
        }}

        IMPORTANT:
        - Enums MUST NOT be declared as valueObjects.
        - ValueObjects MUST contain fields.

        OUTPUT RULES:
        1. Return ONLY the JSON object.
        2. NO Markdown code blocks.
        3. NO explanations or prose.
        4. Use Java 17 compatible types.
        """,
        "expected_output": "Pure raw JSON DNA contract."
    }