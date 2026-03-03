# ai/tasks/heal_code_task.py

def build_heal_code_task(path, context_data="", error_log=None, **kwargs):
    # Recuperamos el log de error de los argumentos o del contexto si no viene
    log = error_log if error_log else kwargs.get('error_log', "Unknown error")
    base_package = kwargs.get('base_package', 'com.application')
    
    return {
        "agent": "backend_builder",
        "description": f"""
        EMERGENCY REPAIR REQUIRED: The file '{path}' failed to compile or pass tests.
        
        MAVEN ERROR LOG:
        '{log}'
        
        CURRENT SOURCE CODE:
        {context_data}
        
        TASK:
        Analyze the error log and the current code. Fix the issue while respecting:
        1. Root Package: '{base_package}'.
        2. Hexagonal Architecture rules.
        3. Proper use of Value Objects and Entity inheritance.
        
        Return ONLY the full corrected source code.
        """,
        "expected_output": "Full corrected Java source code."
    }