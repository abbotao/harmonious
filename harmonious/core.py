from harmonious.registries import StepRegistry

STEP_REGISTRY = StepRegistry()

class TestPlan(object):
    def __init__(self):
        self.name = None
        self.tasks = None

class Task(object):
    def __init__(self):
        self.name = None
        self.description = None
        self.setup_tasks = None
        self.execute_prerequisites = None
        self.glossary = dict()
        self.steps = list()

    def run(self):
        for step in self.steps:
            print "[ %s | %s ]" % (self.name, step.name)
            step.run(self)

class Step(object):
    def __init__(self):
        self.name = None
        self.directions = list()

    def run(self, task):
        for direction in self.directions:
            print direction,
            for (regexp, func) in STEP_REGISTRY.iteritems():
                match = regexp.search(direction)
                if match:
                    result = func(**match.groupdict())
                    if not result:
                        print " FAIL"
                    else:
                        print ""
                    break

