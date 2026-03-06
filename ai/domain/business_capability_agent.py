# ai/domain/business_capability_agent.py

class BusinessCapabilityAgent:
    """
    Derives business capabilities from the domain model.

    Capabilities represent real business actions rather than CRUD operations.
    Example:
        Entity: Invoice
        Capability: GenerateInvoice, SendInvoice
    """

    FINANCIAL_ENTITIES = {"Invoice", "Payment", "Subscription", "Order"}
    LOG_ENTITIES = {"ActivityLog", "Attendance", "AuditLog"}

    def run(self, domain_model):

        dm = domain_model.get("domain_model", domain_model)

        capabilities = []

        for entity in dm.get("entities", []):
            name = entity.get("name")

            if not name:
                continue

            # --- Default creation capability ---
            capabilities.append({
                "name": f"Register{name}",
                "entity": name
            })

            # --- Financial rules ---
            if name in self.FINANCIAL_ENTITIES:
                capabilities.append({
                    "name": f"Generate{name}",
                    "entity": name
                })

                capabilities.append({
                    "name": f"Cancel{name}",
                    "entity": name
                })

            # --- Log / tracking rules ---
            if name in self.LOG_ENTITIES:
                capabilities.append({
                    "name": f"Record{name}",
                    "entity": name
                })

        return capabilities