import yaml

from harmonious.core import TestPlan, Task, Step, TASK_REGISTRY 
import harmonious.selenium_steps

def lower_keys(d):
    if isinstance(d, dict):
        return dict((k.lower(), lower_keys(v)) for k,v in d.iteritems())
    return d

def parse_task_file(filename):
    filehandle = open(filename)
    raw_file = lower_keys(yaml.load(filehandle))

    task = Task(raw_file["name"])
    if "description" in raw_file:
        task.description = raw_file["description"]

    if "prerequisites" in raw_file:
        if "setuptasks" in raw_file["prerequisites"]:
            task.setup_tasks = raw_file["prerequisites"]["setuptasks"]
        if "executeprerequisites" in raw_file["prerequisites"]:
            task.execute_prerequisites = raw_file["prerequisites"]["executeprerequisites"]
    if "glossary" in raw_file:
        for entry in raw_file["glossary"]:
            task.glossary.update(entry)

    for raw_step in raw_file["steps"]:
        step = Step(raw_step.keys()[0])
        for direction in raw_step.values()[0]:
            step.directions.append(direction)
        task.steps.append(step)

    return task

def parse_test_plan(filename):
    filehandle = open(filename)
    raw_file = yaml.load(filehandle)

    test_plans = []
    for item in raw_file:
        testplan = TestPlan(item["name"])
        testplan.tasks = item["tasks"]
        testplan.environment = item["environment"]
        if "variables" in item:
            for entry in item["variables"]:
                testplan.variables.update(entry)
        test_plans.append(testplan)

    return test_plans

def run(test_plan_files, task_files):
    test_plans = []
    for filename in  test_plan_files:
        test_plans.extend(parse_test_plan(filename))

    for filename in task_files:
        task = parse_task_file(filename)
        TASK_REGISTRY[task.name] = task

    for test_plan in test_plans:
        test_plan.run()
