"""ai.agents.semantic_agent

Semantic enrichment wrapper.

main.py calls:
    domain_model = SemanticAgent().run(factory, domain_model)

So the signature MUST be (factory, domain_model).
"""

from ai.domain.semantic_type_detector import detect_semantic_types


class SemanticAgent:
    """Enrich a domain model by inferring semantic/value-object types, aggregates, invariants, etc."""

    name = "semantic"

    def __init__(self, factory=None, logger=None):
        self.factory = factory
        self.logger = logger

    def run(self, factory, domain_model: dict) -> dict:
        # factory is currently unused but kept for consistency and future hooks.
        if self.logger:
            self.logger.info("🧠 SemanticAgent: starting semantic enrichment")

        enriched_model = detect_semantic_types(domain_model)

        if self.logger:
            dm = enriched_model.get("domain_model", enriched_model)
            entities = len(dm.get("entities", []))
            vos = len(dm.get("value_objects", []))
            aggregates = len(dm.get("aggregates", []))
            self.logger.info(
                f"🧠 SemanticAgent: enrichment complete (entities={entities}, value_objects={vos}, aggregates={aggregates})"
            )

        return enriched_model
