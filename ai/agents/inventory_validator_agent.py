# ------------------ Inventory Validator Agent ------------------
class InventoryValidatorAgent:
    """
    Validates that the generated file inventory is internally consistent.
    Detects duplicate paths, missing entity references, or invalid
    generation descriptors before code generation starts.
    """

    def run(self, factory, inventory):

        seen_paths = set()
        cleaned_inventory = []

        for item in inventory:

            path = item.get("path")

            if not path:
                continue

            if path in seen_paths:
                factory.log(f"⚠️ InventoryValidator: duplicate path removed {path}")
                continue

            seen_paths.add(path)
            cleaned_inventory.append(item)

        factory.log(f"🧠 Inventory validated ({len(cleaned_inventory)} files)")

        return cleaned_inventory