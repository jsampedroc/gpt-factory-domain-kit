# ai/tasks/shared_types_task.py

def build_shared_types_task(domain_model, **kwargs):
    return {
        "agent": "architect",
        "description": f"""
        Analyze this Domain Model: {domain_model}
        
        TASK: Identify all generic Shared Enums and common ValueObjects (like Address, ContactInfo).
        
        RULES:
        - Return ONLY a valid JSON object.
        - NO text explanations. NO markdown headers.
        - Structure: {{"enums": [{{"name": "X", "values": "A, B"}}], "value_objects": [{{"name": "Y", "fields": "String f1"}}]}}
        
        CRITICAL: If you cannot find any, return {{"enums": [], "value_objects": []}} but always return a valid JSON.
        """,
        "expected_output": "Strict JSON with enums and value objects."
    }