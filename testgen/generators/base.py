# -*- coding: utf-8 -*-
from abc import ABC, abstractmethod
import json
import logging
import logging.config
import math
import os
import requests


class DataGenerator(ABC):
    def __init__(self, icu_version, run_limit=None):
        self.icu_version = icu_version
        # If set, this is the maximum number of tests generated for each.
        self.run_limit = run_limit

        logging.config.fileConfig("../logging.conf")

    @abstractmethod
    def process_test_data(self):
        pass

    def saveJsonFile(self, filename, data, indent=None):
        output_path = os.path.join(self.icu_version, filename)
        output_file = open(output_path, "w", encoding="UTF-8")
        json.dump(data, output_file, indent=indent)
        output_file.close()

    def getTestDataFromGitHub(self, datafile_name, version):
        # Path for fetching test data from ICU repository
        latest = 'https://raw.githubusercontent.com/unicode-org/icu/main/icu4c/source/test/testdata/"'
        pattern0 = "https://raw.githubusercontent.com/unicode-org/icu/"

        if version == "LATEST":
            ver_string = "main"
        else:
            ver_string = "maint/maint-%s" % version

        pattern1 = "/icu4c/source/test/testdata/"
        url = pattern0 + ver_string + pattern1 + datafile_name
        try:
            r = requests.get(url)
            if r.status_code != 200:
                logging.warning(
                    "Cannot load version %s of file %s", version, datafile_name
                )
                return None
            return r.text
        except BaseException as err:
            logging.warning(
                "Warning: cannot load data %s for version %s. Error = %s",
                datafile_name,
                version,
                err,
            )
            return None

    def sample_tests(self, all_tests):
        if self.run_limit < 0 or len(all_tests) <= self.run_limit:
            return all_tests
        else:
            # Sample to get about run_limit items
            increment = len(all_tests) // self.run_limit
            samples = []
            for index in range(0, len(all_tests), increment):
                samples.append(all_tests[index])
            return samples

    def readFile(self, filename, version=""):
        # If version is provided, it refers to a subdirectory containing the test source
        path = filename
        if version:
            path = os.path.join(version, filename)
        try:
            with open(path, "r", encoding="utf-8") as testdata:
                return testdata.read()
        except BaseException as err:
            logging.warning("** READ: Error = %s", err)
            return None

    def computeMaxDigitsForCount(self, count):
        return math.ceil(math.log10(count + 1))
