class UseCaseGenerator:

    def generate(self, domain_model):

        dm = domain_model.get("domain_model", domain_model)

        entities = dm.get("entities", [])

        usecases = []

        for e in entities:

            name = e["name"]

            usecases.append(f"Create{name}")
            usecases.append(f"Update{name}")
            usecases.append(f"Delete{name}")
            usecases.append(f"Get{name}")

        dm["use_cases"] = usecases

        return domain_model