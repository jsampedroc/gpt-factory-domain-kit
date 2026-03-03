# ai/tasks/audit_code_task.py

def build_audit_code_task(path, base_package, context_data="", **kwargs):
    return {
        "agent": "qa_agent",
        "description": f"""
        Audit the quality and architecture of file '{path}'.
        
        REJECTION CRITERIA:
        1. SYNTAX: Check for 'extends ValueObject' (Error: should be 'implements').
        2. PACKAGES: Ensure package starts with '{base_package}'.
        3. ID DUPLICATION: Reject if an Entity declares its own 'id' field.
        4. MISSING IMPORTS: Check for Lombok or Java Time imports.
        
        CODE TO AUDIT:
        {context_data}
        """,
        "expected_output": "Respond 'APROBADO' or provide a technical error list."
    }