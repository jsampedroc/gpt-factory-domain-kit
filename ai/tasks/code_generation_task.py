# ai/tasks/code_generation_task.py

def build_code_generation_task(path, context_data=None, **kwargs):
    description = kwargs.get('description') or kwargs.get('desc') or "Generate domain-driven logic."
    ctx = context_data or ""
    base_package = kwargs.get('base_package', 'com.application')

    return {
        "agent": "backend_builder",
        "description": f"""
        TASK: Implement Java 17 code for the file: '{path}'
        OBJECTIVE: {description}

        STRICT GAMA ELITE RULES:
        1. SPRING BOOT 3: Use 'jakarta.*' packages (e.g., jakarta.validation.constraints.*). NEVER use 'javax'.
        2. ENUMS: Import all status/types (AppointmentStatus, PatientStatus, etc.) from '{base_package}.domain.shared'.
        3. FLAT ARCHITECTURE: All entities are in '.domain.model'. All IDs are in '.domain.valueobject'.
        4. DTO NAMING: Use suffixes 'Request' or 'Response' (e.g., PatientRequest).

        PROJECT CONTEXT & MAP:
        {ctx}
        """,
        "expected_output": "Clean, compilable Jakarta-compliant Java 17 code."
    }