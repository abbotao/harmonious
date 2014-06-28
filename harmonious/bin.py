import os
import glob
import argparse
import imp

import harmonious


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("path", help="Path to test plans to run")

    args = parser.parse_args()

    if os.path.exists("%s/environment.py"  % args.path):
        imp.load_source("environment", "%s/environment.py" % args.path)

    harmonious.run(glob.glob("%s/*.yml" % args.path), glob.glob("%s/testcases/*.yml" % args.path))
