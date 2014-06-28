from collections import defaultdict
from selenium import webdriver

from harmonious.registries import DIRECTIVE_REGISTRY, TASK_REGISTRY, CALLBACK_REGISTRY
from harmonious.parsers import unquote_variable, is_substitution

from harmonious.exceptions import ImmutableAccessError, StepReturnedFalseError, DirectionUsesReservedWordError


ENVIRONMENT_MAPPING = {
                       'ie': webdriver.Ie,
                       'chrome': webdriver.Chrome,
                       'firefox': webdriver.Firefox,
                       'safari': webdriver.Safari,
                       'opera': webdriver.Opera,
                       'phantom': webdriver.PhantomJS
                       }


class Variables(object):
    def __init__(self):
        self.mutable = defaultdict(lambda: None)
        self.immutable = defaultdict(lambda: None)

    def iterkeys(self):
        for i in self.mutable.iterkeys():
            yield i
        for i in self.immutable.iterkeys():
            yield i

    def itervalues(self):
        for i in self.mutable.itervalues():
            yield i
        for i in self.immutable.itervalues():
            yield i

    def iteritems(self):
        for i in self.mutable.iteritems():
            yield i
        for i in self.immutable.iteritems():
            yield i

    def keys(self):
        return self.mutable.keys() + self.immutable.keys()

    def values(self):
        return self.mutable.values() + self.immutable.values()

    def __contains__(self, item):
        return item in self.mutable or item in self.immutable

    def __len__(self):
        return len(self.mutable) + len(self.immutable)

    def __getitem__(self, key):
        if key in self.mutable:
            return self.mutable[key]
        else:
            # This will raise an error if the item isn't here...
            return self.immutable[key]

    def __setitem__(self, key, value):
        if key in self.immutable:
            raise ImmutableAccessError()

        self.mutable[key] = value

    def __iter__(self):
        for i in self.mutable.iterkeys():
            yield i
        for i in self.immutable.iterkeys():
            yield i

    def define_immutable(self, key, value):
        if key in self.immutable:
            raise ImmutableAccessError()
        if key in self.mutable:
            del self.mutable[key]
        self.immutable[key] = value


class NestedScope(object):
    def __init__(self, global_scope):
        self.scopes = [global_scope]

    def push_scope(self, newscope):
        keyset = set()
        for scope in self.scopes:
            keyset.union(scope.keys())

        shadowed = keyset.intersection(newscope.keys())

        if len(shadowed) > 0:
            print "WARNING: The following variables will be shawdowed in this test set: %s" % shadowed

        self.scopes.append(newscope)

    def pop_scope(self, ):
        self.scopes.pop()

    def __getitem__(self, name):
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]

    def __setitem__(self, name, value):
        for scope in reversed(self.scopes):
            if name in scope:
                scope[name] = value
                return

class Result(dict):
    def __init__(self, name):
        self.name = name
        self.exception = None

class TestPlan(object):
    def __init__(self, name):
        self.name = name
        self.tasks = None
        self.environment = None
        self.variables = Variables()

    def dependency_order(self):
        dependents = defaultdict(list)
        for task in self.tasks:
            dependents[task].extend(TASK_REGISTRY[task].setup_tasks)

        seen = defaultdict(lambda: False)
        for task in self.tasks:
            seen[task] = True
            yield task

            dependent_list = dependents[task]
            while len(dependent_list) > 0:
                current = dependent_list.pop(0)
                if not seen[current]:
                    yield current
                    seen[current] = True
                    dependent_list.extend(dependents[current])

    def run(self):
        results = Result(self.name)
        for task_name in self.dependency_order():
            scope = NestedScope(self.variables)
            browser = ENVIRONMENT_MAPPING[self.environment.lower()]()
            task = TASK_REGISTRY[task_name] 
            for prereq_name in task.execute_prerequisites:
                prereq = TASK_REGISTRY[prereq_name]
                CALLBACK_REGISTRY.run_all(type="task", callback="before", task=prereq)
                CALLBACK_REGISTRY.run_all(type="task", callback="before_output", task=prereq)
                results[prereq.name] = prereq.run(browser, scope)
                CALLBACK_REGISTRY.run_all(type="task", callback="after", task=prereq, result=results[prereq.name])
                CALLBACK_REGISTRY.run_all(type="task", callback="after_output", task=prereq, result=results[prereq.name])

            CALLBACK_REGISTRY.run_all(type="task", callback="before", task=task)
            CALLBACK_REGISTRY.run_all(type="task", callback="before_output", task=task)
            results[task_name] = task.run(browser, scope)
            CALLBACK_REGISTRY.run_all(type="task", callback="after", task=task, result=results[task_name])
            CALLBACK_REGISTRY.run_all(type="task", callback="after_output", task=task, result=results[task_name])
            browser.close()
        return results


class Task(object):
    def __init__(self, name, description=None):
        self.name = name
        self.description = description
        self.setup_tasks = list()
        self.execute_prerequisites = list()
        self.variables = Variables()
        self.steps = list()

    def run(self, browser, scope):
        results = Result(self.name)
        scope.push_scope(self.variables)
        for step in self.steps:
            CALLBACK_REGISTRY.run_all(type="step", callback="before", step=step)
            CALLBACK_REGISTRY.run_all(type="step", callback="before_output", step=step)
            results[step.name] = step.run(browser, scope)
            CALLBACK_REGISTRY.run_all(type="step", callback="after", step=step, result=results[step.name])
            CALLBACK_REGISTRY.run_all(type="step", callback="after_output", step=step, result=results[step.name])
        scope.pop_scope()
        return results


class Step(object):
    def __init__(self, name):
        self.name = name
        self.directions = list()

    def run(self, browser, variables):
        results = Result(self.name)
        for directive in self.directions:
            CALLBACK_REGISTRY.run_all(type="directive", callback="before", directive=directive)
            CALLBACK_REGISTRY.run_all(type="directive", callback="before_output", directive=directive)
            results[directive.string] = directive.run(browser, variables)
            CALLBACK_REGISTRY.run_all(type="directive", callback="after", directive=directive, result=results[directive.string])
            CALLBACK_REGISTRY.run_all(type="directive", callback="after_output", directive=directive, result=results[directive.string])
        return results

class Directive(object):
    def __init__(self, string):
        self.string = string

    def run(self, browser, variables):
        results = Result(self.string)
        for (regexp, func) in DIRECTIVE_REGISTRY.iteritems():
            match = regexp.search(self.string)
            if match:
                # Remove quotes around strings as needed,
                # and substitute variables
                kwargs = match.groupdict()
                for (key, value) in kwargs.iteritems():
                    unquoted = unquote_variable(value)
                    if is_substitution(value):
                        kwargs[key] = variables[unquoted]
                    else:
                        kwargs[key] = unquoted

                # browser is used internally, so let's throw a fit if we already have one
                if "browser" in kwargs:
                    raise DirectionUsesReservedWordError("Direction uses 'browser' which is reserved.")

                kwargs["browser"] = browser
                try:
                    result = func(**kwargs)
                    if result is not None and not result:
                        results.exception = StepReturnedFalseError()
                except Exception as ex:
                    results.exception = ex
                return results