# ai/pipeline/pipeline_engine.py

import time


class PipelineStep:

    def __init__(self, name, fn):
        self.name = name
        self.fn = fn

    def run(self, ctx):
        return self.fn(ctx)


class PipelineEngine:
    """
    Simple declarative pipeline executor so phases can be composed
    without hard-coding everything inside the orchestrator.
    """

    def __init__(self, steps):
        self.steps = steps

    def run(self, ctx):

        results = {}

        for step in self.steps:

            ctx.log(f"▶ Pipeline step: {step.name}")

            start = time.time()

            try:
                results[step.name] = step.run(ctx)

                duration = time.time() - start

                ctx.log(f"✅ Step completed: {step.name} ({duration:.2f}s)")

            except Exception as e:

                duration = time.time() - start

                ctx.log(
                    f"❌ Pipeline step failed: {step.name} "
                    f"after {duration:.2f}s → {e}"
                )

                raise RuntimeError(
                    f"Pipeline failed at step '{step.name}'"
                ) from e

        return results