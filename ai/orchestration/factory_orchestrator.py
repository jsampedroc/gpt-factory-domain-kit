class FactoryOrchestrator:

    def __init__(self, factory):
        self.factory = factory

    def run(self):

        self.factory.log("🧠 Orchestrator started")

        # ---- DOMAIN AGENT ----
        domain_model = self.factory.build_domain_model()

        # ---- SEMANTIC ENGINE ----
        domain_model = self.factory.enrich_domain(domain_model)

        # ---- ARCHITECTURE AGENT ----
        architecture = self.factory.plan_architecture(domain_model)

        # ---- CODE AGENTS ----
        self.factory.generate_code(architecture)

        # ---- VERIFY + COMPILE ----
        self.factory.compile_and_fix()

        self.factory.log("🏁 Orchestrator finished")