# ------------------ Project Planner Agent ------------------

class ProjectPlannerAgent:
    """
    High-level planning agent that can pre-structure the idea before
    the domain modeling phase. This mimics the planning step used in
    systems like Devin / Manus.
    """

    def run(self, factory):
        try:
            plan = factory.executor.run_task(
                "project_planner",
                idea=factory.idea,
                base_package=factory.base_package
            )

            if isinstance(plan, str):
                return json.loads(plan)

            return plan

        except Exception:
            # Planner is optional — fallback to raw idea
            return {"idea": factory.idea}