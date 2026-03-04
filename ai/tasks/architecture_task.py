# ai/tasks/architecture_task.py

def build_architecture_task(domain_kit="", type_registry="", dependency_graph="", **kwargs):
    dk = domain_kit
    return {
        "agent": "architect",
        "description": f"""
ACT AS A SENIOR LEAD ARCHITECT.

DOMAIN MODEL:
{dk}

TYPE REGISTRY (SOURCE OF TRUTH):
{type_registry}

DEPENDENCY GRAPH (SOURCE OF TRUTH):
{dependency_graph}

TASK: Design a COMPLETE Flat Hexagonal inventory.

STRICT RULES FOR PATHS (TOKEN SAVING):
Output ONLY the relative path. DO NOT include 'backend/src/main/java/...' prefix.

ALLOWED PATHS:
- domain/model/EntityName.java
- domain/valueobject/EntityNameId.java
- domain/valueobject/ValueObjectName.java
- domain/shared/EnumName.java
- domain/repository/EntityNameRepository.java
- application/service/EntityNameService.java
- application/dto/EntityNameRequest.java
- application/dto/EntityNameResponse.java
- application/mapper/EntityNameMapper.java
- infrastructure/rest/EntityNameController.java
- infrastructure/persistence/entity/EntityNameJpaEntity.java
- infrastructure/persistence/spring/SpringDataEntityNameRepository.java
- infrastructure/persistence/adapter/JpaEntityNameRepositoryAdapter.java
- test/application/service/EntityNameServiceTest.java

REQUIRED COMPLETENESS:

A) For EVERY entity in TYPE REGISTRY:
   generate ALL layers above for that entity.

B) For EVERY enum in TYPE REGISTRY:
   generate ONE file:
   - domain/shared/EnumName.java
   with description EXACTLY: ENUM

C) For EVERY value_object in TYPE REGISTRY:
   generate ONE file:
   - domain/valueobject/ValueObjectName.java
   with description EXACTLY: ValueObject

CRITICAL:
- Use 1-word descriptions from this allowed set ONLY:
  Entity, ENUM, ValueObject, ID, Repository, Service, DTO_REQUEST, DTO_RESPONSE, Mapper, Controller,
  JPA_ENTITY, SPRING_DATA_REPOSITORY, JPA_ADAPTER, Test
- Return ONLY a raw JSON list:
  [{{"path": "...", "description": "..."}}]
""",
        "expected_output": "Massive relative-path JSON inventory."
    }