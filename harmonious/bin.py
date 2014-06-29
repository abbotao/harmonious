""" Main module for harmonious executable script

Executes harmonious test cases given commandline arguments.

"""
import os
import glob
import argparse
import imp

from harmonious import Runner
from harmonious.core import TASK_REGISTRY
from harmonious.parsers import parse_test_plan, parse_task_file

def main():
    """
    Executes harmonious test cases. Uses argparse, loads the environment script
    for a given folder by filename (to allow loading of callbacks and additional directives),
    and runs the test cases found.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("path", help="Path to test plans to run")

    args = parser.parse_args()

    if os.path.exists("%s/environment.py"  % args.path):
        imp.load_source("environment", "%s/environment.py" % args.path)

    test_plan_files = glob.glob("%s/*.yml" % args.path)

    test_plans = []
    for filename in test_plan_files:
        test_plans.extend(parse_test_plan(filename))

    task_files = glob.glob("%s/testcases/*.yml" % args.path)
    for filename in task_files:
        task = parse_task_file(filename)
        TASK_REGISTRY[task.name] = task

    Runner.run(test_plans)

if __name__ == "__main__":
    main()