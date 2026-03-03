# ai/tasks/architecture_task.py

def build_architecture_task(domain_kit="", **kwargs):
    dk = domain_kit
    return {
        "agent": "architect",
        "description": f"""
        ACT AS A SENIOR LEAD ARCHITECT. 
        Analyze Domain Model: {dk}
        
        TASK: Design a COMPLETE Flat Hexagonal inventory. 
        
        STRICT RULES FOR PATHS (TOKEN SAVING):
        Output ONLY the relative path. DO NOT include 'backend/src/main/java/...' prefix.
        
        EXAMPLES OF ALLOWED PATHS:
        - domain/model/EntityName.java
        - domain/valueobject/EntityNameId.java
        - application/service/EntityNameService.java
        - application/dto/EntityNameRequest.java
        - application/dto/EntityNameResponse.java
        - application/mapper/EntityNameMapper.java
        - infrastructure/rest/EntityNameController.java
        - infrastructure/persistence/JpaEntityNameRepository.java
        - test/application/service/EntityNameServiceTest.java
        
        REQUIRED COMPLETENESS:
        For EVERY Entity identified, generate ALL 9 layers listed above.
        
        CRITICAL: I expect 150+ entries. Use 1-word descriptions (e.g. 'Entity').
        Return ONLY a raw JSON list of dictionaries: [{{"path": "...", "description": "..."}}]
        """,
        "expected_output": "Massive relative-path JSON inventory."
    }