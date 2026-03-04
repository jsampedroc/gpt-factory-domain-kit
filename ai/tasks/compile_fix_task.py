# ai/tasks/compile_fix_task.py

def build_compile_fix_task(error_log=None, **kwargs):

    return {
        "agent": "backend_builder",
        "description": f"""
TASK: Fix Java compilation errors.

COMPILER OUTPUT:
{error_log}

RULES:
- Fix only compilation errors
- Do not modify architecture
- Do not change package names
- Keep Java 17 compatibility
- Do not introduce Lombok
""",
        "expected_output": "Corrected Java code"
    }