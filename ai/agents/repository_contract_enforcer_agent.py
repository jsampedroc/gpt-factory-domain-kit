
# ------------------ Repository Contract Enforcer Agent ------------------
class RepositoryContractEnforcerAgent:
    """
    Ensures that repository ports and adapters share the same method contract.
    Prevents mismatches like:
      save(Entity) -> void  vs  save(Entity) -> Entity
    The agent normalizes repository contracts in the domain model so the
    code generator uses consistent signatures.
    """

    DEFAULT_SAVE_RETURN = "void"

    def run(self, factory, domain_model):

        dm = domain_model.get("domain_model", domain_model)

        # attach repository contract metadata if missing
        if "repository_contract" not in dm:
            dm["repository_contract"] = {}

        for entity in dm.get("entities", []):
            name = entity.get("name")

            dm["repository_contract"][name] = {
                "save_return": self.DEFAULT_SAVE_RETURN
            }

        factory.log(
            f"🧠 Repository contracts normalized for {len(dm.get('entities', []))} entities"
        )

        return domain_model