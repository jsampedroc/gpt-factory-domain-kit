# ai/tasks/project_debug_task.py

def build_project_debug_task(error_log, base_package, **kwargs):
    """
    Analyzes the complete build failure to identify core architectural mismatches.
    """
    return {
        "agent": "qa_agent",
        "description": f"""
        CRITICAL ARCHITECTURAL DIAGNOSIS:
        The project build is failing with multiple errors. 
        
        FILTERED ERROR LOG:
        '{error_log}'
        
        TASK:
        1. Identify exactly why these files are failing (e.g., incorrect base class imports, record syntax errors).
        2. Provide a specific "FIXING MANDATE" for the Principal Architect.
        3. Be extremely technical. If 'ValueObject' is missing an import, specify the full path: {base_package}.domain.shared.ValueObject.
        
        Focus on fixing the foundation to stop the error chain.
        """,
        "expected_output": "A technical mandate to fix the project's core contracts."
    }