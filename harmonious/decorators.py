from harmonious.core import STEP_REGISTRY

def step(regexp, function):
    STEP_REGISTRY.add_step(regexp, function)
    return function

