# ai/tasks/domain_model_task.py

def build_domain_model_task(idea, base_package, **kwargs):
    return {
        "agent": "domain_reasoner",
        "description": f"""
        TASK: Distill the following business idea into a TECHNICAL JSON DNA: '{idea}'
        
        REQUIRED STRUCTURE (STRICT JSON ONLY):
        {{
          "entities": [
            {{
              "name": "Patient",
              "fields": [
                {{"name": "firstName", "type": "String", "constraints": ["NotBlank"]}},
                {{"name": "birthDate", "type": "LocalDate", "constraints": ["NotNull"]}}
              ]
            }}
          ],
          "global_enums": [
              {{ "name": "AppointmentStatus", "values": ["SCHEDULED", "CONFIRMED", "CANCELLED"] }}
          ]
        }}

        RULES:
        1. Return ONLY the JSON object. 
        2. NO Markdown code blocks (DO NOT use ```).
        3. NO conversational text.
        4. Use Java 17 types.
        """,
        "expected_output": "Pure raw JSON DNA contract."
    }