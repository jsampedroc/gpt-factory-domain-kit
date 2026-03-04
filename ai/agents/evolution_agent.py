class EvolutionAgent:
    """
    Decides whether the system should trigger a regeneration cycle
    based on runtime feedback.
    """

    def run(self, factory, runtime_report):

        if not runtime_report:
            return False

        if runtime_report.get("errors"):
            factory.log("🧠 EvolutionAgent detected runtime errors")
            return True

        return False