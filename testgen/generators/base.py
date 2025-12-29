# -*- coding: utf-8 -*-
from abc import ABC, abstractmethod
import codecs
import copy
import hashlib
import json
import logging
import logging.config
import math
import os
import requests

def remove_none(obj):
    # Recursively removes any parts with None as value
    if isinstance(obj, str):
        return obj
    result = copy.copy(obj)
    if hasattr(obj, "items"):
        for (key, value) in obj.items():
            if value is None:
                del result[key]
            else:
                result[key] = remove_none(value)
    elif hasattr(obj, "__iter__"):
        if len(obj) == 1 and obj[0] == obj:
            return result
        for (i, value) in enumerate(obj):
            result[i] = remove_none(value)
    return result

class DataGenerator(ABC):
    def __init__(self, icu_version, run_limit=None):
        self.icu_version = icu_version
        # If set, this is the maximum number of tests generated for each.
        self.run_limit = run_limit

        logging.config.fileConfig("../logging.conf")

    @abstractmethod
    def process_test_data(self):
        pass


    def generateTestHashValues(self, testdata):
        # For each test item, copy it. Omit 'label' from that copy.
        # Create the string representation of that copy with json.dumps()
        # Then make  a hex hash value for that string.
        # Add it to that item.

        try:
            all_tests =  testdata['tests']
        except Exception as error:
            logging.error('# generateTestHashValues: %s does not have "tests": %s',
                          error, testdata.keys())
            return None

        for test in all_tests:
            try:
                test_no_label = test.copy()
            except Exception as error:
                logging.error('error: %s, Item with no label found here: %s, %s' ,
                              error, testdata['test_type'], test)
                continue
            del test_no_label['label']

            # Make it compact and consistent
            test_no_nones = remove_none(test_no_label)
            test_no_label_string = json.dumps(test_no_nones, separators=(',', ':'), sort_keys=True)

            # Create the 32 byte hasn, consisten with Javascript
            hasher = hashlib.sha1()
            hasher.update(test_no_label_string.encode("utf-8"))
            hex_digest = hasher.hexdigest()
            test['hexhash'] = hex_digest

        return True  # Indicates OK

    def saveJsonFile(self, filename, data, indent=None):
        if 'tests' in data:
            hash_ok = self.generateTestHashValues(data)
            if not hash_ok:
                logging.error('### Problems generating hash codes for file %s',
                              filename)

        output_path = os.path.join(self.icu_version, filename)
        # output_file = open(output_path, "w", encoding="utf8")

        with open(output_path, "w", encoding="utf8") as output_file:
            json.dump(data, output_file, indent=indent)

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
        except Exception as err:
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

    def readFile(self, filename, version="", filetype="txt"):
        # If version is provided, it refers to a subdirectory containing the test source
        path = filename
        if version:
            path = os.path.join(version, filename)
        try:
            with codecs.open(path, "r", encoding="utf-8") as testdata:
                return json.load(testdata) if filetype == "json" else testdata.read()
        except Exception as err:
            logging.warning("** readFile: %s", err)
            return None

    def computeMaxDigitsForCount(self, count):
        return math.ceil(math.log10(count + 1))
