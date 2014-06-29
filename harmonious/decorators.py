from harmonious.core import DIRECTIVE_REGISTRY, CALLBACK_REGISTRY
from harmonious.exceptions import ExpectedThrownError

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
                        raise ExpectedThrownError()
            else:
                return func(*args, **kwargs)

        # Add the wrapped function to the registry
        DIRECTIVE_REGISTRY.add_directive(regexp, wrapper)
        return wrapper

    return _step

def expression(regexp):
    def _exp(func):
        DIRECTIVE_REGISTRY.add_directive(regexp, func)
        return func

    return _exp

class Before(object):
    class Output(object):
        @staticmethod
        def all(func):
            CALLBACK_REGISTRY['all']['before_output'].append(func)
            return func

        @staticmethod
        def testplan(func):
            CALLBACK_REGISTRY['testplan']['before_output'].append(func)
            return func

        @staticmethod
        def task(func):
            CALLBACK_REGISTRY['task']['before_output'].append(func)
            return func

        @staticmethod
        def step(func):
            CALLBACK_REGISTRY['step']['before_output'].append(func)
            return func

        @staticmethod
        def directive(func):
            CALLBACK_REGISTRY['directive']['before_output'].append(func)
            return func

    @staticmethod
    def all(func):
        CALLBACK_REGISTRY['all']['before'].append(func)
        return func

    @staticmethod
    def testplan(func):
        CALLBACK_REGISTRY['testplan']['before'].append(func)
        return func

    @staticmethod
    def task(func):
        CALLBACK_REGISTRY['task']['before'].append(func)
        return func

    @staticmethod
    def step(func):
        CALLBACK_REGISTRY['step']['before'].append(func)
        return func

    @staticmethod
    def directive(func):
        CALLBACK_REGISTRY['directive']['before'].append(func)
        return func


class After(object):
    class Output(object):
        @staticmethod
        def all(func):
            CALLBACK_REGISTRY['all']['after_output'].append(func)
            return func

        @staticmethod
        def testplan(func):
            CALLBACK_REGISTRY['testplan']['after_output'].append(func)
            return func

        @staticmethod
        def task(func):
            CALLBACK_REGISTRY['task']['after_output'].append(func)
            return func

        @staticmethod
        def step(func):
            CALLBACK_REGISTRY['step']['after_output'].append(func)
            return func

        @staticmethod
        def directive(func):
            CALLBACK_REGISTRY['directive']['after_output'].append(func)
            return func

    @staticmethod
    def all(func):
        CALLBACK_REGISTRY['all']['after'].append(func)
        return func

    @staticmethod
    def testplan(func):
        CALLBACK_REGISTRY['testplan']['after'].append(func)
        return func

    @staticmethod
    def task(func):
        CALLBACK_REGISTRY['task']['after'].append(func)
        return func

    @staticmethod
    def step(func):
        CALLBACK_REGISTRY['step']['after'].append(func)
        return func

    @staticmethod
    def directive(func):
        CALLBACK_REGISTRY['directive']['after'].append(func)
        return func
