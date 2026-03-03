# ai/tasks/mapper_task.py

def build_mapper_task(path, entity_name, dto_name, base_package, **kwargs):
    return {
        "agent": "backend_builder",
        "description": f"""
        TASK: Create a professional MapStruct Mapper interface for '{entity_name}'.
        PATH: {path}
        
        GOAL: Map between the Domain Entity '{entity_name}' and its DTOs ('{dto_name}Request', '{dto_name}Response').
        
        STRICT ARCHITECTURAL RULES:
        1. SPRING INTEGRATION: Use @Mapper(componentModel = "spring").
        2. FLAT IMPORTS: 
           - Entity: {base_package}.domain.model.{entity_name}
           - ID ValueObject: {base_package}.domain.valueobject.{entity_name}Id
           - DTOs: {base_package}.application.dto.{dto_name}Request/Response
        3. ID MAPPING: Since IDs are Records (ValueObjects), you must provide mapping expressions if the DTO uses primitive types (e.g., UUID or String). 
           Example: @Mapping(target = "id", source = "id.value") 
        4. NESTED OBJECTS: Handle shared types like 'Address' or 'ContactInfo' automatically.
        5. CLEANLINESS: No manual implementation. Only the interface with MapStruct annotations.
        
        PROJECT CONTEXT:
        Ensure the package declaration is exactly: package {base_package}.application.mapper;
        """,
        "expected_output": "A production-ready MapStruct interface with precise @Mapping annotations for DDD ValueObjects."
    }