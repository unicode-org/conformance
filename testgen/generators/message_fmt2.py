# -*- coding: utf-8 -*-
import os
import logging
import glob
from pathlib import Path
from jsonschema import validate, ValidationError
from generators.base import DataGenerator
from test_type import TestType


class MessageFmt2Generator(DataGenerator):
    def process_test_data(self):
        json_test = {"test_type": TestType.MESSAGE_FMT2.value, "tests": []}
        json_verify = {"test_type": TestType.MESSAGE_FMT2.value, "verifications": []}

        src_dir = Path(
            os.path.dirname(__file__),
            "..",
            self.icu_version,
            TestType.MESSAGE_FMT2.value,
        )
        src_file_paths = glob.glob(
            os.path.join(src_dir, "message-format-wg-tests", "**", "*.json"), recursive=True
        )
        src_file_paths.sort()

        json_schema_path = Path(
            os.path.dirname(__file__),
            "..",
            "..",
            "schema",
            TestType.MESSAGE_FMT2.value,
            "testgen_schema.json",
        )
        json_schema = self.readFile(json_schema_path, filetype="json")

        test_count = 0
        test_list = []
        verify_list = []

        skipped_test_count = 0

        for test_file_path in src_file_paths:
            src_data = self.readFile(test_file_path, filetype="json")
            if src_data is None:
                logging.error("testgen/generators/message_fmt2.py: Problem reading JSON. Omitting file %s", test_file_path)
                continue

            defaults = src_data.get("defaultTestProperties")

            # Remove '$schema" before validating and creating tests
            if '$schema' in src_data:
                del src_data['$schema']

            try:
                validate(src_data, json_schema)
            except ValidationError as err:
                logging.error("testgen/generators/message_fmt2.py: JSON %s not validated against schem a %s. Error = %s",
                              test_file_path, json_schema_path, error)

            for src_test in src_data["tests"]:
                test_count += 1

                def from_src_test_or_default(dct, key):
                    if key in src_test:
                        dct[key] = src_test[key]
                    elif key in defaults:
                        dct[key] = defaults[key]

                try:
                    # compute the test case (API inputs info in the form that executors should expect)
                    test = {}
                    test["label"] = f"{test_count - 1:05d}"
                    if "description" in src_test:
                        test["description"] = src_test["description"]
                    test["locale"] = src_test.get("locale") or defaults["locale"]
                    test["src"] = src_test.get("src") or defaults["src"]
                    from_src_test_or_default(test, "params")

                    # compute the verification case (expected return value)
                    verification = {}
                    verification["label"] = test["label"]
                    from_src_test_or_default(verification, "exp")
                    from_src_test_or_default(verification, "expCleanSrc")
                    from_src_test_or_default(verification, "expParts")
                    from_src_test_or_default(verification, "expErrors")

                    # control whether we include the test case
                    # based on whether the test case has a return value (works in this framework)
                    # or whether the test case is expected to trigger an error (skip for now b/c not sure framework is okay with that)
                    if "exp" in verification and verification["exp"] != None:
                        verification["verify"] = verification["exp"]
                        # register the test (API input) & verification (expected value)
                        verify_list.append(verification)
                        test_list.append(test)
                    else:
                        # ignore the test case, so don't record test file entry nor verification file entry
                        skipped_test_count += 1
                        continue
                except KeyError as err:
                    logging.error("testgen/generators/message_fmt2.py: Missing value for %s in %s", err, test_file_path)
                    logging.error("testgen/generators/message_fmt2.py: Omitting test %s", test["label"])

        json_test["tests"] = self.sample_tests(test_list)
        json_verify["verifications"] = self.sample_tests(verify_list)

        self.saveJsonFile(f"{TestType.MESSAGE_FMT2.value}_test.json", json_test, 2)
        self.saveJsonFile(f"{TestType.MESSAGE_FMT2.value}_verify.json", json_verify, 2)

        if test_count > 0:
            logging.info(
                "testgen/generators: MessageFormat2 Test (%s): %d tests processed (of which %d were skipped)",
                self.icu_version,
                test_count,
                skipped_test_count
            )
