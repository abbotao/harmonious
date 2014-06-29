""" Core harmonious classes

This module provides core data types for harmonious test plans.

"""
from collections import defaultdict
from selenium import webdriver

from harmonious.registries import DIRECTIVE_REGISTRY, TASK_REGISTRY, CALLBACK_REGISTRY
from harmonious.utils import unquote_variable, is_substitution

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
    """ Provides a map-like type for both mutable and immutable variables
        Args:

        Attribites:
        mutable: a defaultdict that returns None to store mutable variables
        immutable: a defaultdict that returns None to store immutable variables
    """
    def __init__(self):
        self.mutable = defaultdict(lambda: None)
        self.immutable = defaultdict(lambda: None)

    def iterkeys(self):
        """ Generator to iterate over keys
            Yields: keys stored in mutable, then keys stored in immutable collections
        """
        for i in self.mutable.iterkeys():
            yield i
        for i in self.immutable.iterkeys():
            yield i

    def itervalues(self):
        """ Generator to iterate over values
            Yields: values stored in mutable, then values stored in immutable collections
        """
        for i in self.mutable.itervalues():
            yield i
        for i in self.immutable.itervalues():
            yield i

    def iteritems(self):
        """ Generator to iterate over items
            Yields: items stored in mutable, then items stored in immutable collections
        """
        for i in self.mutable.iteritems():
            yield i
        for i in self.immutable.iteritems():
            yield i

    def keys(self):
        """ Gets the combined set of keys
            Returns: combined keys from mutable and immutable collections
        """
        return self.mutable.keys() + self.immutable.keys()

    def values(self):
        """ Gets the combined set of values
            Returns: combined values from mutable and immutable collections
        """
        return self.mutable.values() + self.immutable.values()

    def __contains__(self, item):
        return item in self.mutable or item in self.immutable

    def __len__(self):
        return len(self.mutable) + len(self.immutable)

    def __getitem__(self, key):
        if key in self.mutable:
            return self.mutable[key]
        else:
            # This will return None if the item isn't here...
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
        """ Setter for immutable values.
            If the key is a mutable variable, will overwrite the mutable variable
            and the variable becomes immutable

            Raises: 
                ImmutableAccessError if the key is already immutable
        """
        if key in self.immutable:
            raise ImmutableAccessError()
        if key in self.mutable:
            del self.mutable[key]
        self.immutable[key] = value


class NestedScope(object):
    """ A class to represent a scope stack, allowing easier resolution of
        variables across scopes from local to global.

        Args:
        global_scope: A ::class::Variables that represents the top most scope.

        Attributes:
        scopes: A list of ::class::Variables objects that represents the scope stack.
    """
    def __init__(self, global_scope):
        self.scopes = [global_scope]

    def push_scope(self, new_scope):
        """ Adds a scope to the current stack
            Args:
            new_scope: The new scope to push onto the stack
        """
        keyset = set()
        for scope in self.scopes:
            keyset.union(scope.keys())

        shadowed = keyset.intersection(new_scope.keys())

        if len(shadowed) > 0:
            print "WARNING: The following variables will be shawdowed in this test set: %s" % shadowed

        self.scopes.append(new_scope)

    def pop_scope(self):
        """ Removes the lowest level (local) scope from the stack. """
        self.scopes.pop()

    def __getitem__(self, name):
        """ Gets the item from the lowest level scope applicable.
            Args:
            name: the name of the variable to retrieve
        """
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]

    def __setitem__(self, name, value):
        """ Sets the item from the lowest level scope applicable.

            Args:
            name: the name of the variable to retrieve
            value: the new value of the item
        """
        for scope in reversed(self.scopes):
            if name in scope:
                scope[name] = value
                return

class Result(dict):
    """ A container class for results from test runs.
        Items stored in the dict are sub-results of the item.
        Args:
        name: Name of the item the result represents

        Attributes:
        name: Name of the item the result represetns
        exception: Any exception caught at this level of the test plan
    """
    def __init__(self, name):
        self.name = name
        self.exception = None

class TestPlan(object):
    """ A class that represents a test plan
        A test plan requires a name.
        Additionally a test plan may contain zero or more "tasks" (which are
        test cases or other series of steps to run), environment information,
        and a collection of variables.

        Args:
        name: the name of the test plan

        Attributes:
        name: the name of the test plan
        tasks: a collection of tasks 
        environment: a structure describing the environment to use for the test
        variables: a collection of variables (this is currently the global scope)
    """
    def __init__(self, name):
        self.name = name
        self.tasks = []
        self.environment = None
        self.variables = Variables()

    def dependency_order(self):
        """ A generator that determines the order of tasks to run given
            the dependencies listed in the tasks
            Yields: ::class::Task objects in order of dependencies
        """
        dependents = defaultdict(list)
        # If we build the dependencies in terms of tasks that depend
        # upon a task in question, we can BFS it to build an execution
        # order that executes things before something that depends on it
        # requires it.
        for task in self.tasks.setup_tasks:
            dependents[task].append(self)

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
        """ Runs the Test plan """
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
    """ A class that represents a task
        A task is a collection of steps (like a test case)
        A task requires a name.
        Additionally a test plan may contain zero or more "steps",
        environment information, an optional description, a list of tasks
        that are prerequisites (must be run before), a list of tasks that
        should be run (always) before this task should be executed and a
        collection of variables.

        Args:
        name: the name of the task
        description: (optional) a description of the task

        Attributes:
        name: the name of the task
        description: description of the task
        setup_tasks: pre-requisite tasks that must be run once
        execute_prerequisites: tasks that must be run every time before this one
        steps: a collection of steps to run 
        variables: a collection of variables (this is currently the global scope)
    """
    def __init__(self, name, description=None):
        self.name = name
        self.description = description
        self.setup_tasks = list()
        self.execute_prerequisites = list()
        self.variables = Variables()
        self.steps = list()

    def run(self, browser, scope):
        """ Runs the task """
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
    """ A class that represents a step
        A step is a collection of directives
        A step requires a name.
        Additionally a step contains zero or more "directives".

        Args:
        name: the name of the task

        Attributes:
        name: the name of the task
        directives: the directives to run as part of this step
    """
    def __init__(self, name):
        self.name = name
        self.directions = list()

    def run(self, browser, variables):
        """ Runs the step """
        results = Result(self.name)
        for directive in self.directions:
            CALLBACK_REGISTRY.run_all(type="directive", callback="before", directive=directive)
            CALLBACK_REGISTRY.run_all(type="directive", callback="before_output", directive=directive)
            results[directive.string] = directive.run(browser, variables)
            CALLBACK_REGISTRY.run_all(type="directive", callback="after", directive=directive, result=results[directive.string])
            CALLBACK_REGISTRY.run_all(type="directive", callback="after_output", directive=directive, result=results[directive.string])
        return results

class Directive(object):
    """ A class that represents a directive
        A directive is a string that will be bound (via regexp) to execute the individual item

        Args:
        string: the string for this directive 

        Attributes:
        string: the string for this directive 
    """
    def __init__(self, string):
        self.string = string

    def run(self, browser, variables):
        """ Runs the directive """
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