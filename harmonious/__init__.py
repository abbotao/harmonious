from harmonious.core import CALLBACK_REGISTRY
from harmonious.parsers import parse_variable, parse_test_plan, parse_task_file

import harmonious.selenium_directives, harmonious.output.color_console

class Runner(object):
    def run(test_plans):
        CALLBACK_REGISTRY.run_all(type="all", callback="before")
        CALLBACK_REGISTRY.run_all(type="all", callback="before_output")
        results = []
        for test_plan in test_plans:
            results.append(test_plan.run())
        CALLBACK_REGISTRY.run_all(type="all", callback="after")
        CALLBACK_REGISTRY.run_all(type="all", callback="after_output", results=results)