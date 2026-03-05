class PipelineEngine:

    def __init__(self, steps):
        self.steps = steps

    def run(self, ctx):

        for step in self.steps:
            step.run(ctx)