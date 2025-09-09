# -*- coding: utf-8 -*-
import argparse
import logging
import logging.config
import multiprocessing as mp
import re

from test_type import TestType, test_types
from generators.collation import CollationGenerator
from generators.datetime_fmt import DateTimeFmtGenerator
from generators.localeDisplayNames import LocaleNamesGenerator
from generators.likely_subtags import LikelySubtagsGenerator
from generators.message_fmt2 import MessageFmt2Generator
from generators.list_fmt import ListFmtGenerator
from generators.number_fmt import NumberFmtGenerator
from generators.plurals import PluralGenerator
from generators.relativedatetime_fmt import RelativeDateTimeFmtGenerator
from generators.segmenter import SegmenterGenerator


def setupArgs():
    parser = argparse.ArgumentParser(prog="testdata_gen")
    parser.add_argument("--icu_versions", nargs="*", default=[])
    parser.add_argument(
        "--test_types", nargs="*", choices=test_types, default=test_types
    )
    # -1 is no limit
    parser.add_argument("--run_limit", nargs="?", type=int, default=-1)
    new_args = parser.parse_args()
    return new_args


def generate_versioned_data_parallel(args):
    num_processors = mp.cpu_count()
    logging.info(
        "Test data generation: %s processors for %s plans",
        num_processors,
        len(args.icu_versions),
    )

    version_data = []
    for icu_version in args.icu_versions:
        version_data.append({"icu_version": icu_version, "args": args})

    processor_pool = mp.Pool(num_processors)
    with processor_pool as p:
        result = p.map(generate_versioned_data, version_data)

    return result


def generate_versioned_data(version_info):
    args = version_info["args"]
    icu_version = version_info["icu_version"]

    logging.info(
        "Generating .json files for data driven testing. ICU_VERSION requested = %s",
        icu_version,
    )

    if len(args.test_types) < len(TestType):
        logging.info("(Only generating %s)", ", ".join(args.test_types))

    if TestType.COLLATION in args.test_types:
        # This is slow
        generator = CollationGenerator(icu_version, args.run_limit)
        generator.process_test_data()

    ## DISABLED FOR NOW. Use new .js generator with Node version
    if TestType.DATETIME_FMT in args.test_types:
        # This is slow
        generator = DateTimeFmtGenerator(icu_version, args.run_limit)
        generator.process_test_data()

    if TestType.LIST_FMT in args.test_types:
        # This is slow
        generator = ListFmtGenerator(icu_version, args.run_limit)
        generator.process_test_data()

    if TestType.LANG_NAMES in args.test_types:
        generator = LocaleNamesGenerator(icu_version, args.run_limit)
        if generator:
            generator.process_test_data()

    if TestType.LIKELY_SUBTAGS in args.test_types:
        generator = LikelySubtagsGenerator(icu_version, args.run_limit)
        generator.process_test_data()

    if TestType.MESSAGE_FMT2 in args.test_types:
        generator = MessageFmt2Generator(icu_version, args.run_limit)
        generator.process_test_data()

    if TestType.NUMBER_FMT in args.test_types:
        generator = NumberFmtGenerator(icu_version, args.run_limit)
        generator.process_test_data()

    if TestType.RELATIVE_DATETIME_FMT in args.test_types:
        # This is slow
        generator = RelativeDateTimeFmtGenerator(icu_version, args.run_limit)
        generator.process_test_data()

    if TestType.PLURAL_RULES in args.test_types:
        # This is slow
        generator = PluralGenerator(icu_version, args.run_limit)
        generator.process_test_data()

    if TestType.SEGMENTER in args.test_types:
        # This is slow
        generator = SegmenterGenerator(icu_version, args.run_limit)
        generator.process_test_data()

    logging.info("++++ Data generation for %s is complete.", icu_version)


def main():
    new_args = setupArgs()

    logger = logging.Logger("TEST_GENERATE LOGGER")
    logger.setLevel(logging.INFO)

    # Generate version data in parallel if possible
    generate_versioned_data_parallel(new_args)


if __name__ == "__main__":
    main()
