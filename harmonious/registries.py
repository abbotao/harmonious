import re

class StepRegistry(dict):
    def add_step(self, regexp, step_func):
        self.steps[re.compile(regexp)] = step_func