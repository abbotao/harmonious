from collections import defaultdict
from selenium import webdriver

from harmonious.registries import StepRegistry

STEP_REGISTRY = StepRegistry()
TASK_REGISTRY = defaultdict(lambda: None)

ENVIRONMENT_MAPPING = { 
    'ie': webdriver.Ie, 
    'chrome': webdriver.Chrome, 
    'firefox': webdriver.Firefox,
    'safari': webdriver.Safari,
    'opera': webdriver.Opera,
    'phantom': webdriver.PhantomJS
}

class TestPlan(object):
    def __init__(self, name):
        self.name = None
        self.tasks = None
        self.environment = None
        self.variables = defaultdict(lambda: None)

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
            browser = ENVIRONMENT_MAPPING[self.environment.lower()]()
            for prereq in TASK_REGISTRY[task].execute_prerequisites:
                TASK_REGISTRY[prereq].run(browser, self.variables)
            TASK_REGISTRY[task].run(browser, self.variables)
            browser.close()

class Task(object):
    def __init__(self, name, description=None):
        self.name = name
        self.description = description
        self.setup_tasks = list()
        self.execute_prerequisites = list()
        self.glossary = defaultdict(lambda: None)
        self.steps = list()

    def run(self, browser, global_glossary):
        glossary = self.glossary.copy()
        glossary.update(global_glossary)
        for step in self.steps:
            print "[ %s | %s ]" % (self.name, step.name)
            step.run(browser, glossary)

class Step(object):
    def __init__(self, name):
        self.name = name
        self.directions = list()

    def run(self, browser, glossary):
        for direction in self.directions:
            print "  -",direction,
            for (regexp, func) in STEP_REGISTRY.iteritems():
                match = regexp.search(direction)
                if match:
                    kwargs = match.groupdict()
                    for (key, value) in kwargs.iteritems():
                        if value[0] == "[" and value[-1] == "]":
                            #if value[1:-1] not in glossary: we should do something here
                            kwargs[key] = glossary[value[1:-1]]
                    kwargs["browser"] = browser
                    try:
                        result = func(**kwargs)
                    except:
                        print "... FAIL",
                    finally:
                        print ""
