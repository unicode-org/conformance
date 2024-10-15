import argparse
import subprocess
import sys
from testgen import testdata_gen
from testdriver import ddtargs


def main():
    args = parse_args()

    if args.command == "testgen":
        subprocess.run(["python3", "testdata_gen.py"] + sys.argv[2:], cwd="testgen")

    if args.command == "test":
        subprocess.run(["python3", "testdriver.py"] + sys.argv[2:], cwd="testdriver")


def parse_args():
    parser = argparse.ArgumentParser()

    subparsers = parser.add_subparsers(dest="command")

    testgen_parser = subparsers.add_parser("testgen")
    testdata_gen.setup_args(testgen_parser)

    test_parser = subparsers.add_parser("test")
    ddtargs.setup_common_args(test_parser)
    ddtargs.setup_testdriver_args(test_parser)

    return parser.parse_args()
