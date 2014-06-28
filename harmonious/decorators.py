from harmonious.core import DIRECTIVE_REGISTRY, CALLBACK_REGISTRY
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

        # Add the wrapped function to the registry
        DIRECTIVE_REGISTRY.add_directive(regexp, wrapper)
        return wrapper

    return _step


class Before(object):
    class Output(object):
        def all(func):
            CALLBACK_REGISTRY['all']['before_output'] = func
            return func

        def testplan(func):
            CALLBACK_REGISTRY['testplan']['before_output'] = func
            return func

        def task(func):
            CALLBACK_REGISTRY['task']['before_output'] = func
            return func

        def step(func):
            CALLBACK_REGISTRY['step']['before_output'] = func
            return func

        def directive(func):
            CALLBACK_REGISTRY['directive']['before_output'] = func
            return func


    def all(func):
        CALLBACK_REGISTRY['all']['before'] = func
        return func

    def testplan(func):
        CALLBACK_REGISTRY['testplan']['before'] = func
        return func

    def task(func):
        CALLBACK_REGISTRY['task']['before'] = func
        return func

    def step(func):
        CALLBACK_REGISTRY['step']['before'] = func
        return func

    def directive(func):
        CALLBACK_REGISTRY['directive']['before'] = func
        return func


class After(object):
    class AfterOutput(object):
        def all(func):
            CALLBACK_REGISTRY['all']['after_output'] = func
            return func

        def testplan(func):
            CALLBACK_REGISTRY['testplan']['after_output'] = func
            return func

        def task(func):
            CALLBACK_REGISTRY['task']['after_output'] = func
            return func

        def step(func):
            CALLBACK_REGISTRY['step']['after_output'] = func
            return func

        def directive(func):
            CALLBACK_REGISTRY['directive']['after_output'] = func
            return func


    def all(func):
        CALLBACK_REGISTRY['all']['after'] = func
        return func

    def testplan(func):
        CALLBACK_REGISTRY['testplan']['after'] = func
        return func

    def task(func):
        CALLBACK_REGISTRY['task']['after'] = func
        return func

    def step(func):
        CALLBACK_REGISTRY['step']['after'] = func
        return func

    def directive(func):
        CALLBACK_REGISTRY['directive']['after'] = func
        return func
