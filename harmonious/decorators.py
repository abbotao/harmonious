from functools import wraps

from harmonious.core import DIRECTIVE_REGISTRY
from harmonious.exceptions import ExpectedThrownException

def directive(regexp, throws=None):
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
        DIRECTIVE_REGISTRY.add_directive(regexp, wrapper)
        return wrapper

    return _step

