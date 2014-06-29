from harmonious.core import CALLBACK_REGISTRY

import harmonious.selenium_directives, harmonious.output.color_console

class Runner(object):
    @staticmethod
    def run(test_plans):
        CALLBACK_REGISTRY.run_all(type="all", callback="before")
        CALLBACK_REGISTRY.run_all(type="all", callback="before_output")
        results = []
        for test_plan in test_plans:
            CALLBACK_REGISTRY.run_all(type="testplan", callback="before", test_plan=test_plan)
            CALLBACK_REGISTRY.run_all(type="testplan", callback="before_output", test_plan=test_plan)
            result = test_plan.run()
            CALLBACK_REGISTRY.run_all(type="testplan", callback="after", test_plan=test_plan, result=result)
            CALLBACK_REGISTRY.run_all(type="testplan", callback="after_output", test_plan=test_plan, result=result)
            results.append(result)
        CALLBACK_REGISTRY.run_all(type="all", callback="after", results=results)
        CALLBACK_REGISTRY.run_all(type="all", callback="after_output", results=results)