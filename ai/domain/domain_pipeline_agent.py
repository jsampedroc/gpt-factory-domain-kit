

"""
DomainPipelineAgent
-------------------

This agent encapsulates the entire *domain reasoning pipeline* that was
previously living inside `main.py`.

The goal is to keep `main.py` focused only on orchestration while all
business/domain reasoning lives in dedicated agents.
"""


class DomainPipelineAgent:

    def __init__(
        self,
        domain_agent,
        semantic_agent,
        aggregate_detector,
        bounded_context_detector,
        module_architecture_agent,
        capability_agent,
        usecase_planner,
        type_discovery_engine,
        domain_graph_builder,
        semantic_code_graph_builder,
        spec_graph_builder,
        deterministic_spec_generator,
        code_planner,
    ):

        self.domain_agent = domain_agent
        self.semantic_agent = semantic_agent
        self.aggregate_detector = aggregate_detector
        self.bounded_context_detector = bounded_context_detector
        self.module_architecture_agent = module_architecture_agent
        self.capability_agent = capability_agent
        self.usecase_planner = usecase_planner
        self.type_discovery_engine = type_discovery_engine
        self.domain_graph_builder = domain_graph_builder
        self.semantic_code_graph_builder = semantic_code_graph_builder
        self.spec_graph_builder = spec_graph_builder
        self.deterministic_spec_generator = deterministic_spec_generator
        self.code_planner = code_planner

    def run(self, factory):
        """
        Executes the full domain discovery + planning pipeline.
        """

        # ------------------------------
        # 1. Base domain discovery
        # ------------------------------
        domain_model = self.domain_agent.run(factory)

        # ------------------------------
        # 2. Semantic enrichment
        # ------------------------------
        domain_model = self.semantic_agent.run(factory, domain_model)

        # ------------------------------
        # 3. Aggregate detection
        # ------------------------------
        aggregates = self.aggregate_detector.run(domain_model)

        # ------------------------------
        # 4. Bounded contexts
        # ------------------------------
        contexts = self.bounded_context_detector.run(domain_model)

        # ------------------------------
        # 5. Module architecture
        # ------------------------------
        modules = self.module_architecture_agent.run(domain_model, contexts)

        # ------------------------------
        # 6. Business capabilities
        # ------------------------------
        capabilities = self.capability_agent.run(domain_model)

        # ------------------------------
        # 7. Use cases
        # ------------------------------
        use_cases = self.usecase_planner.run(capabilities)

        # ------------------------------
        # 8. Type discovery
        # ------------------------------
        domain_model = self.type_discovery_engine.run(domain_model)

        # ------------------------------
        # 9. Domain graph
        # ------------------------------
        domain_graph = self.domain_graph_builder.run(domain_model)

        # ------------------------------
        # 10. Semantic code graph
        # ------------------------------
        semantic_code_graph = self.semantic_code_graph_builder.run(domain_model)

        # ------------------------------
        # 11. Spec graph
        # ------------------------------
        spec_graph = self.spec_graph_builder.run(domain_model)

        # ------------------------------
        # 12. Deterministic spec
        # ------------------------------
        spec = self.deterministic_spec_generator.run(domain_model)

        # ------------------------------
        # 13. Code plan
        # ------------------------------
        code_plan = self.code_planner.run(domain_model, use_cases)

        return {
            "domain_model": domain_model,
            "aggregates": aggregates,
            "contexts": contexts,
            "modules": modules,
            "capabilities": capabilities,
            "use_cases": use_cases,
            "domain_graph": domain_graph,
            "semantic_code_graph": semantic_code_graph,
            "spec_graph": spec_graph,
            "spec": spec,
            "code_plan": code_plan,
        }