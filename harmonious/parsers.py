import yaml

from harmonious.utils import unquote_variable
from harmonious.core import TestPlan, Task, Step, Directive

def lower_keys(dictionary):
    if isinstance(dictionary, dict):
        return dict((key.lower(), lower_keys(value)) for key, value in dictionary.iteritems())
    return dictionary

def parse_variable(var):
    parts = var.split("=")
    if len(parts) > 0:
        return (parts[0], unquote_variable(parts[1]))
    else:
        return var

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

    if "variables" in raw_file:
        for entry in raw_file["variables"]:
            for key, value in entry.iteritems():
                task.variables[key] = parse_variable(value)
    if "glossary" in raw_file:
        for entry in raw_file["glossary"]:
            for key, value in entry.iteritems():
                task.variables.define_immutable(key, parse_variable(value))

    for raw_step in raw_file["steps"]:
        step = Step(raw_step.keys()[0])
        for direction in raw_step.values()[0]:
            step.directions.append(Directive(string=direction))
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
                for key, value in entry.iteritems():
                    testplan.variables[key] = parse_variable(value)
        if "glossary" in item:
            for entry in item["glossary"]:
                for key, value in entry.iteritems():
                    testplan.variables.define_immutable(key, parse_variable(value))
        test_plans.append(testplan)

    return test_plans