import argparse
import sys
from testgen import testdata_gen
from testdriver import testdriver, ddtargs


def main():
    args = parse_args()

    if args.command == "testgen":
        testdata_gen.main(sys.argv[1:])

    if args.command == "test":
        # FIXME
        testdriver.main(sys.argv[1:])


def parse_args():
    parser = argparse.ArgumentParser()

    subparsers = parser.add_subparsers(dest="command")

    testgen_parser = subparsers.add_parser("testgen")
    testdata_gen.setup_args(testgen_parser)

    test_parser = subparsers.add_parser("test")
    ddtargs.setup_args(test_parser)

    return parser.parse_args()
