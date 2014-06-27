import glob
import argparse

import harmonious


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("path", help="Path to test plans to run")

    args = parser.parse_args()

    harmonious.run(glob.glob("%s/*.yml" % args.path), glob.glob("%s/testcases/*.yml" % args.path))
