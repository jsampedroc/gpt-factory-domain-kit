# ai/domain/semantic_domain_agent.py

from ai.domain.semantic_type_detector import detect_semantic_types


class SemanticDomainAgent:
    """
    Performs semantic enrichment of the domain model.
    Delegates the low-level detection to semantic_type_detector.
    """

    def run(self, domain_model: dict) -> dict:
        try:
            enriched = detect_semantic_types(domain_model)
            return enriched
        except Exception:
            # Fail-safe: return original model
            return domain_model