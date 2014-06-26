import re

class StepRegistry(dict):
    def add_step(self, regexp, step_func):
        self[re.compile(regexp, flags=re.IGNORECASE)] = step_func