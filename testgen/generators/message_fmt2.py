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
            os.path.join(src_dir, "**", "*.json"), recursive=True
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

        for test_file_path in src_file_paths:
            src_data = self.readFile(test_file_path, filetype="json")
            if src_data is None:
                logging.error("Problem reading JSON. Omitting file %s", test_file_path)
                continue

            defaults = src_data.get("defaultTestProperties")

            try:
                validate(src_data, json_schema)
            except ValidationError as err:
                logging.error("Problem validating JSON: %s", test_file_path)
                logging.error(err)

            for src_test in src_data["tests"]:
                test_count += 1
                label = f"{test_count - 1:05d}"
                description = f'{src_data["scenario"]}: {src_test["description"]}'
                args = src_test.get("args") or (
                    defaults.get("args") if defaults else None
                )

                try:
                    test_list.append(
                        {
                            "label": label,
                            "test_description": description,
                            "test_subtype": src_test.get("testSubtype")
                            or defaults["testSubtype"],
                            "locale": src_test.get("locale") or defaults["locale"],
                            "pattern": src_test.get("pattern") or defaults["pattern"],
                            **({"args": args} if args else {}),
                        }
                    )
                    verify_list.append({"label": label, "verify": src_test["verify"]})
                except KeyError as err:
                    logging.error("Missing value for %s in %s", err, test_file_path)
                    logging.error("Omitting test %s (%s)", label, description)

        json_test["tests"] = self.sample_tests(test_list)
        json_verify["verifications"] = self.sample_tests(verify_list)

        print(json_test)

        self.saveJsonFile(f"{TestType.MESSAGE_FMT2}_test.json", json_test, 2)
        self.saveJsonFile(f"{TestType.MESSAGE_FMT2}_verify.json", json_verify, 2)

        logging.info(
            "MessageFormat2 Test (%s): %d tests processed", self.icu_version, test_count
        )
