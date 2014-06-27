from functools import wraps

from harmonious.core import STEP_REGISTRY
from harmonious.exceptions import ExpectedThrownException

import pdb

def direction(regexp, throws=None):
    def _step(func):
        def wrapper(*args, **kwargs):
            if throws:
                thrown = False
                try:
                    return func(*args, **kwargs)
                except throws:
                    thrown = True
                finally:
                    if not thrown:
                        raise ExpectedThrownException()
            else:
                return func(*args, **kwargs)

        #Add the wrapped function to the registry
        STEP_REGISTRY.add_step(regexp, wrapper)
        return wrapper

    return _step

