
"""
Semantic Agent

Responsible for enriching the raw domain model using the semantic
analysis pipeline (DDD pattern detection, aggregates, invariants,
domain graph, value objects, etc.).
"""

from ai.domain.semantic_type_detector import detect_semantic_types


class SemanticAgent:
    """
    Agent responsible for semantic enrichment of the domain model.

    Input:
        Raw domain model produced by the DomainAgent.

    Output:
        Enriched domain model containing:
            - semantic types
            - value objects
            - aggregates
            - domain events
            - invariants
            - domain graph
            - architecture hints
            - learning signals
    """

    def __init__(self, logger=None):
        self.logger = logger

    def run(self, domain_model: dict) -> dict:
        """
        Execute semantic enrichment.

        Parameters
        ----------
        domain_model : dict
            Raw domain model produced by the domain reasoning step.

        Returns
        -------
        dict
            Enriched domain model.
        """

        if self.logger:
            self.logger.info("🧠 SemanticAgent: starting semantic enrichment")

        enriched_model = detect_semantic_types(domain_model)

        if self.logger:
            entities = len(enriched_model.get("entities", []))
            vos = len(enriched_model.get("value_objects", []))
            aggregates = len(enriched_model.get("aggregates", []))

            self.logger.info(
                f"🧠 SemanticAgent: enrichment complete "
                f"(entities={entities}, value_objects={vos}, aggregates={aggregates})"
            )

        return enriched_model