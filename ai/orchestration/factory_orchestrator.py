class FactoryOrchestrator:

    def __init__(self, factory):
        self.factory = factory

    def run(self):

        self.factory.log("🧠 Orchestrator started")

        # ---- PLANNER AGENT ----
        plan = self.factory.plan_project()

        # ---- DOMAIN AGENT ----
        domain_model = self.factory.build_domain_model(plan)

        # ---- KNOWLEDGE AGENT (Domain Knowledge Engine) ----
        domain_model = self.factory.apply_domain_knowledge(domain_model)

        # ---- SEMANTIC ENGINE ----
        domain_model = self.factory.enrich_domain(domain_model)

        # ---- ARCHITECTURE AGENT ----
        architecture = self.factory.plan_architecture(domain_model)

        # ---- DEPENDENCY GRAPH (ORDER GENERATION) ----
        nodes, edges = self.factory.build_dependency_graph(architecture)
        ordered = self.factory.sort_dependency_graph(nodes, edges)
        architecture["ordered_inventory"] = ordered

        # ---- CODE AGENTS ----
        self.factory.generate_code(architecture)

        # ---- SELF-HEALING COMPILE LOOP ----
        MAX_FIX_ATTEMPTS = 5

        for attempt in range(MAX_FIX_ATTEMPTS):

            result = self.factory.compile_project()

            if result.get("success"):
                self.factory.log("✅ Compilation successful")
                break

            self.factory.log(
                f"⚠️ Compilation failed (attempt {attempt+1}/{MAX_FIX_ATTEMPTS})"
            )

            self.factory.apply_code_fixes(result)

        else:
            raise RuntimeError("Compilation failed after maximum fix attempts")

        self.factory.log("🏁 Orchestrator finished")