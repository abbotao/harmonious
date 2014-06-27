from collections import defaultdict
from selenium import webdriver

from harmonious.registries import DIRECTIVE_REGISTRY, TASK_REGISTRY
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
            #This will raise an error if the item isn't here...
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

class TestPlan(object):
    def __init__(self, name):
        self.name = None
        self.tasks = None
        self.environment = None #TODO: we should allow more details here than just browser named...
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
        for task in self.dependency_order():
            scope = NestedScope(self.variables)
            browser = ENVIRONMENT_MAPPING[self.environment.lower()]()
            for prereq in TASK_REGISTRY[task].execute_prerequisites:
                TASK_REGISTRY[prereq].run(browser, scope)
            TASK_REGISTRY[task].run(browser, scope)
            browser.close()

class Task(object):
    def __init__(self, name, description=None):
        self.name = name
        self.description = description
        self.setup_tasks = list()
        self.execute_prerequisites = list()
        self.glossary = Variables()
        self.steps = list()

    def run(self, browser, scope):
        scope.push_scope(self.glossary)
        for step in self.steps:
            print "[ %s | %s ]" % (self.name, step.name)
            step.run(browser, scope)
        scope.pop_scope()

class Step(object):
    def __init__(self, name):
        self.name = name
        self.directions = list()

    def run(self, browser, glossary):
        for direction in self.directions:
            print "  -",direction,
            for (regexp, func) in DIRECTIVE_REGISTRY.iteritems():
                match = regexp.search(direction)
                if match:
                    #Remove quotes around strings as needed,
                    #and substitute variables
                    kwargs = match.groupdict()
                    for (key, value) in kwargs.iteritems():
                            unquoted = unquote_variable(value)
                            if is_substitution(value):
                                kwargs[key] = glossary[unquoted]
                            else:
                                kwargs[key] = unquoted
                    #browser is used internally, so let's throw a fit if we already have one
                    if "browser" in kwargs:
                        raise DirectionUsesReservedWordError("Direction uses 'browser' which is reserved.")

                    kwargs["browser"] = browser
                    try:
                        result = func(**kwargs)
                        if result is not None and not result:
                            raise StepReturnedFalseError()
                    except:
                        print "... FAIL",
                    finally:
                        print ""
