# ai/tasks/audit_task.py

def build_audit_task(path, content, error_log, global_context, **kwargs):
    # Recuperamos el paquete base dinámicamente
    base_package = kwargs.get('base_package', 'com.application')
    
    return {
        "agent": "principal_architect",
        "description": f"""
        TASK: YOU ARE THE MASTER LEAD ARCHITECT & CODE AUDITOR. 
        Your mission is to perform a surgical fix on a broken Java file.
        
        FILE TO REPAIR: {path}
        BASE PACKAGE: {base_package}

        --- 🚨 MAVEN ERROR LOG (The Problem) ---
        {error_log}

        --- 📚 THE SOURCE OF TRUTH (GLOBAL PROJECT SIGNATURES) ---
        This JSON contains the EXACT fields and method names that exist in other classes. 
        {global_context}

        --- 🛠️ REPAIR PROTOCOL ---
        1. MAPPER PROPERTIES (CRITICAL):
           - If Maven says 'Unknown property' or 'No property named', look at the 'fields' of the Entity and the DTO in the SOURCE OF TRUTH.
           - Adjust the @Mapping annotations to match the REAL field names.
           - Example: If the Truth says 'fullName' but the DTO uses 'name', use @Mapping(source="fullName", target="name").

        2. SIGNATURE ALIGNMENT: 
           - Cross-reference every method call with the 'methods' in the SOURCE OF TRUTH.
           - Rename any mismatched method calls to match the existing ones.
        
        3. FLAT ARCHITECTURE:
           - Imports MUST follow: {base_package}.domain.model.*, {base_package}.domain.valueobject.*, etc.
           - REMOVE sub-packages like .domain.patient.* or .port.inbound.*.

        4. SPRING BOOT 3 & JAKARTA:
           - Always use 'jakarta.*' packages.

        5. ZERO LOGIC CHANGE:
           - Only fix the "wiring" (imports, property names, and signatures).

        OUTPUT ONLY THE FULL UPDATED SOURCE CODE. NO EXPLANATIONS. NO MARKDOWN WRAPPERS.
        """,
        "expected_output": "Perfectly wired Java 17 source code, synchronized with all existing project properties and methods."
    }