# ai/agents/code_generation_agent.py

class CodeGenerationAgent:
    """
    Centralizes all Java code generation logic.

    This agent decides whether a file should be generated using:
    - AST generator (for domain entities / deterministic structures)
    - Template generator (for infrastructure / controllers / services)
    - LLM generation (fallback for complex cases)

    Keeping this logic outside the orchestrator keeps `main.py`
    focused only on pipeline orchestration.
    """

    def __init__(self, ast_generator, template_generator, executor):
        self.ast_generator = ast_generator
        self.template_generator = template_generator
        self.executor = executor

    def generate(self, factory, item):
        """
        Main entrypoint used by the orchestrator.

        Parameters
        ----------
        factory : SoftwareFactory
            Access to configuration and paths
        item : dict
            Inventory item describing the file to generate
        """

        rel_path = item["path"]
        desc = item.get("description")
        entity = item.get("entity")
        fields = item.get("fields", [])

        # --------------------------------------------------
        # DOMAIN MODEL → deterministic AST generation
        # --------------------------------------------------
        if desc == "Entity":
            return self.ast_generator.generate_entity(
                base_package=factory.base_package,
                entity_name=entity,
                fields=fields,
            )

        if desc == "ID Record":
            return self.ast_generator.generate_value_object(
                base_package=factory.base_package,
                vo_name=f"{entity}Id",
            )

        # --------------------------------------------------
        # INFRASTRUCTURE → deterministic templates
        # --------------------------------------------------
        if desc == "JPA_ENTITY":
            package = factory.base_package + ".infrastructure.persistence.entity"
            return self.template_generator.generate_jpa_entity(
                package_name=package,
                class_name=f"{entity}JpaEntity",
                fields=fields,
            )

        if desc == "SPRING_DATA_REPOSITORY":
            package = factory.base_package + ".infrastructure.persistence.spring"
            return self.template_generator.generate_repository(
                package_name=package,
                entity=entity,
            )

        if desc == "Service":
            package = factory.base_package + ".application.service"
            return self.template_generator.generate_service(
                package_name=package,
                class_name=f"{entity}Service",
                entity=entity,
                base_package=factory.base_package,
            )

        if desc == "Controller":
            package = factory.base_package + ".infrastructure.rest"
            return self.template_generator.generate_controller(
                package_name=package,
                class_name=f"{entity}Controller",
                entity=entity,
                base_package=factory.base_package,
            )

        # --------------------------------------------------
        # FALLBACK → LLM generation
        # --------------------------------------------------
        return self.executor.run_task(
            "write_code",
            path=rel_path,
            base_package=factory.base_package,
            context_data=item,
        )
