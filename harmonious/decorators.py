from harmonious.core import STEP_REGISTRY

def step(regexp):
    def _step(func):
        STEP_REGISTRY.add_step(regexp, func)
        return func

    return _step

