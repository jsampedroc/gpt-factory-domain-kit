# ai/tasks/arbitration_task.py

def build_arbitration_task(path, error_log, context_data="", base_package="com.application", **kwargs):
    return {
        "agent": "principal_architect",
        "description": f"""
        URGENT ARCHITECTURAL FIX REQUIRED: '{path}'.
        This file is causing a recursive error loop in the project build.
        
        MAVEN ERROR CONTEXT:
        '{error_log}'
        
        TASK:
        As Principal Architect, rewrite this file to be 100% compilable.
        1. Resolve any 'Symbol not found' by checking the standard Hexagonal structure.
        2. Ensure all ValueObjects are records and Entities extend the correct base class.
        3. STRICT PACKAGE: '{base_package}'.
        4. If a dependency is missing, simplify the logic so it doesn't depend on ungenerated code.
        
        Do not allow the build to fail again because of this file.
        """,
        "expected_output": "Final, verified, and compilable Java source code."
    }