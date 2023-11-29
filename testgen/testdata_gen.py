# -*- coding: utf-8 -*-

import argparse
import json
import logging
import logging.config
import math
import os
import re
import requests
import sys

reblankline = re.compile('^\s*$')

# Global constants
# Values to be formatted in number format tests
NUMBERS_TO_TEST = ['0', '91827.3645', '-0.22222']

# Which locales are selected for this testing.
# This selects es-MX, zh-TW, bn-BD
NUMBERFORMAT_LOCALE_INDICES = [3, 7, 11]


class generateData():
    def __init__(self, icu_version):
        self.icu_version = icu_version
        # If set, this is the maximum number of tests generated for each.
        self.run_limit = None

        logging.config.fileConfig("../logging.conf")

    def setVersion(self, selected_version):
        self.icu_version = selected_version

    def saveJsonFile(self, filename, data, indent=None):
      output_path = os.path.join(self.icu_version, filename)
      output_file = open(output_path, 'w')
      json.dump(data, output_file, indent=indent)
      output_file.close()


    def getTestDataFromGitHub(self, datafile_name, version):
        # Path for fetching test data from ICU repository
        latest = 'https://raw.githubusercontent.com/unicode-org/icu/main/icu4c/source/test/testdata/"'
        pattern0 = 'https://raw.githubusercontent.com/unicode-org/icu/'

        if version == 'LATEST':
            ver_string = 'main'
        else:
            ver_string = 'maint/maint-%s' % version

        pattern1 = '/icu4c/source/test/testdata/'
        url = pattern0 + ver_string + pattern1 + datafile_name
        try:
            r = requests.get(url)
            if r.status_code != 200:
                logging.warning('Cannot load version %s of file %s', version, datafile_name)
                return None
            return r.text
        except BaseException as err:
            logging.warning('Warning: cannot load data %s for version %s. Error = %s', datafile_name, version, err)
            return None

    def processCollationTestData(self):
        # Get each kind of collation tests and create a unified data set
        json_test = {'test_type': 'collation_short',
                     'tests':[]}
        json_verify = {'test_type': 'collation_short',
                       'verifications': []}
        insert_collation_header([json_test, json_verify])

        start_count = 0

        # Data from more complex tests in github's unicode-org/icu repository
        # icu4c/source/test/testdata/collationtest.txt
        test_complex, verify_complex = generateCollTestData2(
            'collationtest.txt',
            self.icu_version,
            ignorePunctuation=False,
            start_count=len(json_test['tests']))

        if verify_complex:
            json_verify['verifications'].extend(verify_complex)

        if test_complex:
            json_test['tests'].extend(test_complex)

        # Collation ignoring punctuation
        test_ignorable, verify_ignorable =  generateCollTestDataObjects(
            'CollationTest_SHIFTED_SHORT.txt',
            self.icu_version,
            ignorePunctuation=True,
            start_count=len(json_test['tests']))

        json_test['tests'].extend(test_ignorable)
        json_verify['verifications'].extend(verify_ignorable)

        # Collation considering punctuation
        test_nonignorable, verify_nonignorable = generateCollTestDataObjects(
            'CollationTest_NON_IGNORABLE_SHORT.txt',
            self.icu_version,
            ignorePunctuation=False,
            start_count=len(json_test['tests']))

        # Resample as needed
        json_test['tests'].extend(test_nonignorable)
        json_test['tests'] = self.sample_tests(json_test['tests'])

        json_verify['verifications'].extend(verify_nonignorable)
        json_verify['verifications'] = self.sample_tests(json_verify['verifications'])

        # And write the files
        self.saveJsonFile('collation_test.json', json_test)
        self.saveJsonFile('collation_verify.json', json_verify)

    def processNumberFmtTestData(self):
        filename = 'dcfmtest.txt'
        rawdcmlfmttestdata = readFile(filename, self.icu_version)
        if rawdcmlfmttestdata:
            BOM = '\xef\xbb\xbf'
            if rawdcmlfmttestdata.startswith(BOM):
                logging.info('Skip BOM')
                rawdcmlfmttestdata = rawdcmlfmttestdata[3:]

        filename = 'numberpermutationtest.txt'
        rawnumfmttestdata = readFile(filename, self.icu_version)
        if rawnumfmttestdata:
            num_testdata_object_list, num_verify_object_list, count = generateNumberFmtTestDataObjects(rawnumfmttestdata)
            if rawdcmlfmttestdata:
                dcml_testdata_object_list, dcml_verify_object_list, count = generateDcmlFmtTestDataObjects(rawdcmlfmttestdata, count)

            test_list = num_testdata_object_list + dcml_testdata_object_list
            verify_list = num_verify_object_list + dcml_verify_object_list
            json_test, json_verify = insertNumberFmtDescr(test_list, verify_list)

            json_test['tests'] = self.sample_tests(json_test['tests'])
            json_verify['verifications'] = self.sample_tests(json_verify['verifications'])

            self.saveJsonFile('num_fmt_test_file.json', json_test)

            output_path = os.path.join(self.icu_version, 'num_fmt_verify_file.json')
            num_fmt_verify_file = open(output_path, 'w')
            json.dump(json_verify, num_fmt_verify_file, indent=1)
            num_fmt_verify_file.close()

            logging.info('NumberFormat Test (%s): %s tests created', self.icu_version, count)
        return

    def processLangNameTestData(self):
        json_test = {'test_type': 'lang_names'}
        json_verify = {'test_type': 'lang_names'}
        languageNameDescr(json_test, json_verify)
        filename = 'languageNameTable.txt'
        rawlangnametestdata = readFile(filename, self.icu_version)

        if not rawlangnametestdata:
            return None

        # TODO: add standard vs. dialect vs. alternate names
        self.generateLanguageNameTestDataObjects(rawlangnametestdata, json_test, json_verify)
        output_path = os.path.join(self.icu_version, 'lang_name_test_file.json')
        lang_name_test_file = open(output_path, 'w')
        json.dump(json_test, lang_name_test_file, indent=1)
        lang_name_test_file.close()


        output_path = os.path.join(self.icu_version, 'lang_name_verify_file.json')
        lang_name_verify_file = open(output_path, 'w')
        json.dump(json_verify, lang_name_verify_file, indent=1)
        lang_name_verify_file.close()

        return True

    def generateLanguageNameTestDataObjects(self, rawtestdata, json_tests, json_verify):
      # Get the JSON data for tests and verification for language names
      recommentline = re.compile('^\s*#')
      count = 0

      jtests = []
      jverify = []

      # Compute max size needed for label number
      test_lines = rawtestdata.splitlines()
      num_samples = len(test_lines)
      max_digits = computeMaxDigitsForCount(num_samples)
      for item in test_lines:
        if not (recommentline.match(item) or reblankline.match(item)):
          test_data = parseLanguageNameData(item)
          if test_data == None:
            logging.warning('  LanguageNames (%s): Line \'%s\' not recognized as valid test data entry', self.icu_version, item)
            continue
          else:
            label = str(count).rjust(max_digits, '0')
            test_json = {'label': label, 'language_label': test_data[0], 'locale_label': test_data[1]}
            jtests.append(test_json)
            jverify.append({'label': label, 'verify': test_data[2]})
            count += 1

      json_tests['tests'] = self.sample_tests(jtests)
      json_verify['verifications'] = self.sample_tests(jverify)

      logging.info('LangNames Test (%s): %d lines processed', self.icu_version, count)
      return

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

    def processLikelySubtagsData(self):

        filename = 'likelySubtags.txt'
        file_version = '2023-08-17, https://github.com/unicode-org/cldr/pull/3176'
        raw_likely_subtags_data = readFile(filename, self.icu_version)
        if not raw_likely_subtags_data:
            return None

        json_test = {'test_type': 'likely_subtags',
                     'source_file': filename,
                     'source_version': file_version,
                     'tests': []}
        json_verify = {'test_type': 'likely_subtags',
                     'source_file': filename,
                     'source_version': file_version,
                       }
        json_verify['Test Scenario'] = json_test['Test scenario'] = 'likely_subtags'
        # Generate the test and verify json
        testlines = raw_likely_subtags_data.splitlines()
        count = 0
        max_digits = computeMaxDigitsForCount(len(testlines))
        test_list = []
        verify_list = []
        for line in testlines:
            # Ignore blank and # comment lineslines()
            if len(line) == 0 or line[0] == "#":
                continue
            # split at ";" and ignore whitespace
            tags = list(map(str.strip, line.split(';')))

            # Normalize to 4 tags: Source; AddLikely; RemoveFavorScript; RemoveFavorRegin
            while len(tags) < 4:
                tags.append('')
            if not tags[2]:
                tags[2] = tags[1]
            if not tags[3]:
                tags[3] = tags[2]

            # Create minimize tests - default is RemoveFavorScript
            source = tags[0]
            add_likely = tags[1]
            remove_favor_script = tags[2]
            remove_favor_region = tags[3]

            # And maximize from each tag
            label = str(count).rjust(max_digits, '0')
            test_max = {'label': label,
                        'locale': source,
                        'option': 'maximize'
                        }
            verify = {'label': label,
                      'verify': add_likely
                      }
            test_list.append(test_max)
            verify_list.append(verify)
            count += 1

            # Expected minimized form favoring the script
            label = str(count).rjust(max_digits, '0')
            test_min = {'label': label,
                        'locale': source,
                        'option': 'minimize'
                        }
            verify = {'label': label,
                      'verify': remove_favor_script
                      }
            test_list.append(test_min)
            verify_list.append(verify)
            count += 1

            # And check for minimizing with favored region is supported
            label = str(count).rjust(max_digits, '0')
            test_favor_region = {'label': label,
                                 'locale': source,
                                 'option': 'minimizeFavorRegion'
                                 }
            verify = {'label': label,
                      'verify': remove_favor_region
                      }
            test_list.append(test_favor_region)
            verify_list.append(verify)
            count += 1

        # Add to the test and verify json data
        json_test['tests'] = self.sample_tests(test_list)
        json_verify['verifications'] = self.sample_tests(verify_list)

        # Output the files including the json dump
        self.saveJsonFile('likely_subtags_test.json', json_test)
        self.saveJsonFile('likely_subtags_verify.json', json_verify)
        logging.info('Likely Subtags Test (%s): %d lines processed', self.icu_version, count)
        return


# Utility functions
def computeMaxDigitsForCount(count):
    return math.ceil(math.log10(count + 1))


def readFile(filename, version=''):
    # If version is provided, it refers to a subdirectory containing the test source
    path = filename
    if version:
        path = os.path.join(version, filename)
    try:
        with open(path, 'r', encoding='utf8') as testdata:
            return testdata.read()
    except BaseException as err:
        logging.warning('** Cannot read file %s. Error = %s', path, err)
        return None


def parseCollTestData(testdata):
  testdata = testdata.encode().decode('unicode_escape')
  recodepoint = re.compile(r'[0-9a-fA-F]{4,6}')

  return_list= []
  codepoints = recodepoint.findall(testdata)
  for code in codepoints:
      num_code = int(code, 16)
      if num_code >= 0xd800 and num_code <= 0xdfff:
          return None
      return_list.append(stringifyCode(num_code))
  return ''.join(return_list)

def parseDcmlFmtTestData(rawtestdata):
  reformat = re.compile(r'format +([\d.E@\#]+) +(default|ceiling|floor|down|up|halfeven|halfdown|halfup|unnecessary) +\"(-?[\d.E]+)\" +\"(-?[\d.E]+|Inexact)\"')
  # TODO: ignore 'parse' line
  try:
      test_match = reformat.search(rawtestdata)
  except AttributeError as error:
      logging.warning('** parseDcmlFmtTestData: %s', error)
  if not test_match:
      logging.warning('No test match with rawtestdata = %s', rawtestdata)

  return test_match.group(1), test_match.group(2), test_match.group(3), test_match.group(4)


def mapFmtSkeletonToECMA402(options):
  ecma402_map = {
      "compact-short": {"notation": "compact",  "compactDisplay": "short"},
      "scientific/+ee/sign-always": {"notation": "scientific"},
      # Percent with word "percent":
      "percent": {"style": "unit", "unit": "percent"},  # "style": "percent",
      "currency/EUR": {"style": "currency", "currencyDisplay": "symbol",  "currency": "EUR"},
      "measure-unit/length-meter": {"style": "unit",  "unit": "meter"},
      "measure-unit/length-furlong": {"style": "unit", "unit": "furlong"},
      "unit-width-narrow": {"unitDisplay": "narrow", "currencyDisplay": "narrowSymbol"},
      "unit-width-full-name": {"unitDisplay": "long", "currencyDisplay": "name"},
      #"unit-width-full-name": {"unitDisplay": "long"},
      "precision-integer": {"maximumFractionDigits": 0, "minimumFractionDigits": 0, "roundingType": "fractionDigits"},
      ".000": {"maximumFractionDigits": 3, "minimumFractionDigits": 3},

      # Use maximumFractionDigits: 2, maximumSignificantDigits: 3, roundingPriority: "morePrecision"
      ".##/@@@+": {"maximumFractionDigits": 2, "maximumSignificantDigits": 3,"roundingPriority": "morePrecision"},
      "@@": {"maximumSignificantDigits": 2, "minimumSignificantDigits": 2},
      "rounding-mode-floor": {"roundingMode": "floor"},
      "integer-width/##00": {"maximumIntegerDigits": 4, "minimumIntegerDigits":2},
      "group-on-aligned": {"useGrouping": True},
      "latin": {"numberingSystem": "latn"},
      "sign-accounting-except-zero": {"signDisplay": "exceptZero", "currencySign": "accounting"},
      # These are all patterns...
      "0.0000E0": {"notation": "scientific", "minimumIntegerDigits": 1, "minimumFractionDigits": 4, "maximumFractionDigits": 4},
      "00": {"minimumIntegerDigits":2, "maximumFractionDigits":0},
      "#.#": {"maximumFractionDigits": 1},
      "@@@": {"minimumSignificantDigits": 3, "maximumSignificantDigits": 3},
      "@@###": {"minimumSignificantDigits": 2, "maximumSignificantDigits": 5},
      "@@@@E0": {"notation": "scientific", "minimumSignificantDigits": 4, "maximumSignificantDigits": 4},
      "0.0##E0": {"notation": "scientific", "minimumIntegerDigits":1, "minimumFractionDigits": 1, "maximumFractionDigits": 3},
      "00.##E0": {"notation": "scientific", "minimumIntegerDigits":2, "minimumFractionDigits": 1, "maximumFractionDigits": 3},
      "0005": {"minimumIntegerDigits":2},
      "0.00": {"minimumIntegerDigits":1, "minimumFractionDigits": 2, "maximumFractionDigits": 2},
      "0.000E0": {"notation": "scientific", "minimumIntegerDigits":1, "minimumFractionDigits": 3, "maximumFractionDigits": 3},
      "0.0##": {"minimumIntegerDigits":1, "minimumFractionDigits": 1, "maximumFractionDigits": 3},
      "#": {"minimumIntegerDigits":1, "maximumFractionDigits": 0},
      "0.#E0": {"notation": "scientific", "minimumIntegerDigits":1, "maximumFractionDigits": 1},
      "0.##E0": {"notation": "scientific", "minimumIntegerDigits":1, "maximumFractionDigits": 2},
      ".0E0": {"notation": "scientific", "minimumFractionDigits": 1, "maximumFractionDigits": 1},
      ".0#E0": {"notation": "scientific", "minimumFractionDigits": 1, "maximumFractionDigits": 2},
      "@@@@@@@@@@@@@@@@@@@@@@@@@": {"minimumSignificantDigits": 21, "maximumSignificantDigits": 21},
      "0.0": {"minimumIntegerDigits":1, "minimumFractionDigits": 1, "maximumFractionDigits": 1}
      }

  ecma402_options = []

  options_dict = {}
  # Which combinatins of skeleton entries need modificiation?
  # Look at the expected output...
  for o in options:
    if o != 'scale/0.5' and o != 'decimal-always':
      option_detail = ecma402_map[o]
      options_dict = options_dict | option_detail
    if o[0:5] == "scale":
        options_dict = options_dict | {"conformanceScale": o[6:]}
    if o == "decimal-always":
        options_dict = options_dict | {"conformanceDecimalAlways": True}

   # TODO: resolve some combinations of entries that are in conflict
  return  options_dict


def mapRoundingToECMA402(rounding):
  ecma402_rounding_map = {
      "default": 'halfEven',
      "halfeven": 'halfEven',
      "halfodd": 'none',
      "halfdown": 'halfTrunc',
      "halfup": 'halfExpand',
      "down": 'trunc',
      "up": 'expand',
      "halfceiling": 'halfCeil',
      "halffloor": 'halfFloor',
      "floor": 'floor',
      "ceiling": 'ceil',
      "unnecessary": "unnecessary"
      }
  return ecma402_rounding_map[rounding]


def parseNumberFmtTestData(rawtestdata):
  renumformat = re.compile(r'([\w/@\+\-\#\.]+) ([\w/@\+\-\#\.]+) ([\w/@\+\-\#\.]+)\n\s*(\w\w\-\w\w)\n\s*(.*?)\n\s*(.*?)\n\s*(.*?)\n\s*(\w\w\-\w\w)\n\s*(.*?)\n\s*(.*?)\n\s*(.*?)\n\s*(\w\w\-\w\w)\n\s*(.*?)\n\s*(.*?)\n\s*(.*?)\n')

  return renumformat.findall(rawtestdata)


def parseLanguageNameData(rawtestdata):
  reformat = re.compile(r'(\w*);(\w*);(.*)')

  test_match = reformat.search(rawtestdata)

  if test_match != None:
    return (test_match.group(1), test_match.group(2), test_match.group(3))
  else:
    return None


def generateNumberFmtTestDataObjects(rawtestdata, count=0):
  # Returns 2 lists JSON-formatted: all_tests_list, verify_list
  original_count = count
  entry_types = {
      "compact-short": "notation",
      "scientific/+ee/sign-always": "notation",
      "percent": "unit",
      "currency/EUR": "unit",  ## TODO: Change the unit
      "measure-unit/length-meter": "unit",
      "measure-unit/length-furlong": "unit",
      "unit-width-narrow": "unit-width",
      "unit-width-full-name": "unit-width",
      "precision-integer": "precision",
      ".000": "precision",
      ".##/@@@+": "precision",
      "@@": "precision",
      "rounding-mode-floor": "rounding-mode",
      "integer-width/##00": "integer-width",
      "scale/0.5": "scale",
      "group-on-aligned": "grouping",
      "latin": "symbols",
      "sign-accounting-except-zero": "sign-display",
      "decimal-always": "decimal-separator-display"
      }
  test_list = parseNumberFmtTestData(rawtestdata)
  ecma402_options_start = ['"options": {\n']

  all_tests_list = []
  verify_list = []

  expected_count = len(test_list) * len(NUMBERFORMAT_LOCALE_INDICES) * len(NUMBERS_TO_TEST) + count
  max_digits = computeMaxDigitsForCount(expected_count)
  logging.info('  Expected count  of number fmt tests: %s', expected_count)

  for test_options in test_list:
    # The first three specify the formatting.
    # Example: compact-short percent unit-width-full-name
    part1 = entry_types[test_options[0]]
    part2 = entry_types[test_options[1]]
    part3 = entry_types[test_options[2]]

    # TODO: use combinations of part1, part2, and part3 to generate options.
    # Locales are in element 3, 7, and 11 of parsed structure.

    for locale_idx in NUMBERFORMAT_LOCALE_INDICES:
      for number_idx in range(len(NUMBERS_TO_TEST)):
        ecma402_options = []
        label = str(count).rjust(max_digits, '0')
        expected = test_options[locale_idx + 1 + number_idx]
        verify_json = {'label': label, 'verify': expected}
        verify_list.append(verify_json)

        # TODO: Use JSON module instead of print formatting
        skeleton = '%s %s %s' % (test_options[0], test_options[1], test_options[2])
        entry = {'label': label,
                 'locale': test_options[locale_idx],
                 'skeleton': skeleton,
                 'input': NUMBERS_TO_TEST[number_idx]
                 }

        try:
            options_dict = mapFmtSkeletonToECMA402([test_options[0], test_options[1], test_options[2]])
        except KeyError as error:
            logging.warning('Looking up Skeletons: %s [0-2] = %s, %s %s', error,
                            test_options[0], test_options[1], test_options[2])
        if not options_dict:
            logging.warning('$$$ OPTIONS not found for %s', label)
        # TODO: Look at the items in the options_dict to resolve conflicts and set up things better.
        resolved_options_dict = resolveOptions(options_dict, test_options)
        # include these options in the entry
        entry = entry | {'options': resolved_options_dict}

        all_tests_list.append(entry)  # All the tests in JSON form
        count += 1
  logging.info('  generateNumberFmtTestDataObjects gives %d tests',
               (count - original_count))
  return all_tests_list, verify_list, count


def resolveOptions(raw_options, skeleton_list):
    # Resolve conflicts with options before putting them into the test's options.
    # TODO: fix all the potential conflicts
    resolved = raw_options
    if 'minimumSignificantDigits' in resolved and 'maximumFractionDigits' in resolved:
        resolved.pop('minimumSignificantDigits')

    # Set up default maximumFractionDigits if if not compact or currency
    if ('maximumFractionDigits' not in resolved and
        ('notation' not in resolved or resolved['notation'] != 'compact') and
        ('style' not in resolved or resolved['style'] != 'currency')):
        resolved['maximumFractionDigits'] = 6

    if skeleton_list and 'percent' in skeleton_list:
        resolved['style'] = 'unit'
        resolved['unit'] = 'percent'
    if skeleton_list and 'unit-width-full-name' in skeleton_list:
        resolved['currencyDisplay'] = 'name'
        resolved['unitDisplay'] = 'long'
    return resolved


# Count is the starting point for the values
# Use older Decimal Format specifications
# Source data: https://github.com/unicode-org/icu/blob/main/icu4c/source/test/testdata/dcfmtest.txt
def generateDcmlFmtTestDataObjects(rawtestdata, count=0):
  original_count = count
  recommentline = re.compile('^\s*#')
  test_list = rawtestdata.splitlines()

  all_tests_list = []
  verify_list = []

  expected = len(test_list) + count
  logging.info('  expected count = %s', (len(test_list) -1))
  max_digits = computeMaxDigitsForCount(expected)

  for item in test_list[1:]:
    if not (recommentline.match(item) or reblankline.match(item)):
      # Ignore parse for now.
      if item[0:5] == "parse":
          continue
      pattern, round_mode, test_input, expected = parseDcmlFmtTestData(item)
      rounding_mode = mapRoundingToECMA402(round_mode)
      label = str(count).rjust(max_digits, '0')
      entry = {'label': label, 'skeleton': pattern , 'input': test_input, 'options': {} }

      json_part = mapFmtSkeletonToECMA402([pattern])

      resolved_options_dict = resolveOptions(json_part, None)
      # None of these old patterns use groupings
      resolved_options_dict['useGrouping'] = False

      if rounding_mode:
          entry['options']['roundingMode'] = rounding_mode
      else:
          # Default if not specified
          entry['options']['roundingMode'] = ecma402_rounding_map['halfeven']

      entry['options'] |= resolved_options_dict  # ??? json_part

      all_tests_list.append(entry)
      verify_list.append({'label': label,
                          'verify': expected})
      count += 1

  logging.info('  generateDcmlFmtTestDataObjects gives %d tests',
               (count - original_count))
  return all_tests_list, verify_list, count


def stringifyCode(cp):
    # Converts some code points represented as hex strings to escaped values, others as characters
    if cp < 0x20 or cp == 0x22 or cp == 127 or cp == 0x5c:
        teststring = '\\u' + format(cp, '04x')
    else:
        try:
            teststring = chr(cp)
        except ValueError as err:
            teststring = cp

    return teststring


def generateCollTestData2(filename,
                          icu_version,
                          ignorePunctuation,
                          start_count=0):
    # Read raw data from complex test file, e.g., collation_test.txt
    test_list, verify_list = None, None

    label_num = start_count

    encode_errors = []

    test_list = []
    verify_list = []

    rawcolltestdata = readFile(filename, icu_version)
    if not rawcolltestdata:
        return test_list, verify_list

    raw_testdata_list = rawcolltestdata.splitlines()
    max_digits = 1 + computeMaxDigitsForCount(len(raw_testdata_list))  # Approximate
    recommentline = re.compile('^[\ufeff\s]*#(.*)')

    root_locale = re.compile('@ root')
    locale_string = re.compile('@ locale (\S+)')
    test_line = re.compile('^\*\* test:(.*)')
    rule_header_pattern = re.compile('^@ rules')
    rule_pattern = re.compile('^&.*')

    compare_pattern = re.compile('^\* compare(.*)')

    comparison_pattern = re.compile('(\S+)\s+(\S+)\s*(\#?.*)')  # compare operator followed by string

    attribute_test = re.compile('^\% (\S+)\s*=\s*(\S+)')
    rules = ''

    # Ignore comment lines
    string1 = ''
    string2 = ''
    attributes = []
    test_description = ''

    # Get @ root or @ locale ...
    # Check for "@ rules"
    # Handle % options, e.g., strengt=h, reorder=, backwards=, caseFirst=,
    #  ...
    # Find "* compare" section and create list of tests for this,
    # starting comparison with empty string ''.
    # Handle compre options =, <, <1, <2, <3, <4

    locale = ''
    line_number = 0
    num_lines = len(raw_testdata_list)
    while line_number < num_lines:
        line_in = raw_testdata_list[line_number]
        line_number += 1

        is_comment = recommentline.match(line_in)
        if line_in[0:1] == '#' or is_comment or reblankline.match(line_in):
            continue

        if root_locale.match(line_in):
            locale = 'und'
            continue
        locale_match = locale_string.match(line_in)
        if locale_match:
            locale = locale_match.group(1)
            continue

        # Find "** test" section
        is_test =  test_line.match(line_in)
        if is_test:
            test_description = is_test.group(1)
            rules = []
            tests_for_test = []
            locale = ''
            attributes = []
            continue

        # Handle rules, to be applied in subsequent tests
        is_rules = rule_header_pattern.match(line_in)
        if is_rules:
            # Read rule lines until  a "*" line is found
            rules = []
            # Skip comment and empty lines
            while line_number < num_lines:
                if line_number >= num_lines:
                    break
                line_in = raw_testdata_list[line_number]
                if len(line_in) == 0 or line_in[0] == '#':
                    line_number += 1
                    continue
                if line_in[0] == '*':
                    break
                # Remove any comments in the line preceded by '#'
                comment_start = line_in.find('#')
                if comment_start >= 0:
                    line_in = line_in[0:comment_start]
                rules.append(line_in.strip())
                line_number += 1
            continue

        is_compare = compare_pattern.match(line_in)
        if is_compare:
            compare_mode = True
            info = is_compare.group(1)
            while line_number < num_lines:
                line_number += 1
                if line_number >= num_lines:
                    break
                line_in = raw_testdata_list[line_number]

                if len(line_in) == 0 or line_in[0] == '#':
                    continue
                if line_in[0] == '*':
                    break

                is_comparison = comparison_pattern.match(line_in)
                # Handle compare options =, <, <1, <2, <3, <4
                if is_comparison:
                    compare_type = is_comparison.group(1)
                    compare_string = is_comparison.group(2)
                    # Note that this doesn't seem to handle \x encoding, howeveer.
                    string2 = compare_string.encode().decode('unicode_escape')
                    compare_comment = is_comparison.group(3)
                    # Generate the test case
                    try:
                        s = compare_string.encode()
                        string2 = s.decode('unicode_escape')
                        #string2 = compare_string.encode().decode('unicode_escape')
                    except UnicodeEncodeError as err:
                        logging.error('%s: line: %d. PROBLEM ENCODING', err, line_number)
                        continue

                    compare_comment = is_comparison.group(3)

                    label = str(label_num).rjust(max_digits, '0')
                    label_num += 1
                    test_case = {
                        'label': label,
                        's1': string1,
                        'compare_type': compare_type,
                        'test_description': test_description
                    }

                    # If either string has unpaired surrogates, ignore the case, with a warning
                    if check_unpaired_surrogate_in_string(string2):
                        # String 1 is the previous, already checked
                        try:
                            #logging.warning('!!! generateCollTestData2: file%s: Unmatched surrogate ignored in line %s: s1: %s, s2: %s',
                            #                file_name, line_number, string1, compare_string)
                            encode_errors.append([line_number, compare_string])
                        except UnicodeEncodeError as err:
                            logging.error('!!! Line %s encoding error: %s', err)

                        string2 = compare_string
                        test_case['warning'] = 'unpaired surrogate in test case - not decoded'

                    else:
                        string2 = compare_string.encode().decode('unicode_escape')

                    test_case['s2'] = string2

                    # Add info to the test case.
                    if locale:
                        test_case['locale'] = locale
                    # Keep this for the next comparison test
                    string1 = string2
                    if compare_comment:
                       test_case['compare_comment'] = compare_comment
                    if rules:
                        test_case['rules'] = '\n'.join(rules)
                    if attributes:
                        test_case['attributes'] = attributes
                    test_list.append(test_case)
                    verify_list.append({
                        'label': label,
                        'verify': True
                    })
                    # Just to record which ones belong to this test
                    tests_for_test.append(test_case)
            continue

        is_attribute = attribute_test.match(line_in)
        if is_attribute:
            attributes.append([is_attribute.group(1), is_attribute.group(2)])
            continue
    if encode_errors:
        logging.warning('!! %s File %s has DATA ERRORS: %s',
                        filename, len(encode_errors), encode_errors)
    return test_list, verify_list


def check_unpaired_surrogate_in_string(text):
    # Look for unmatched high/low surrogates in the text
    high_surrogate_pattern = re.compile(r'([\ud800-\udbff])')
    low_surrogate_pattern = re.compile(r'([\udc00-\udfff])')

    match_high = high_surrogate_pattern.findall(text)
    match_low = low_surrogate_pattern.findall(text)

    if not match_high and not match_low:
        return False

    if match_high and not match_low:
        return True

    if not match_high and match_low:
        return True

    # TODO: Check if each high match is immediately followed by a low match
    # Now, assume that they are paired
    return False



    return False

def generateCollTestDataObjects(filename,
                                icu_version,
                                ignorePunctuation,
                                start_count=0):
    # Read raw data
    rawcolltestdata = readFile(filename, icu_version)

    if not rawcolltestdata:
        return None, None

    raw_testdata_list = rawcolltestdata.splitlines()

    # Handles lines of strings to be compared with collation.
    # Adds field for ignoring punctuation as needed.
    recommentline = re.compile('^\s*#')

    test_list = []
    verify_list = []

    max_digits = 1 + computeMaxDigitsForCount(len(raw_testdata_list))  # Approximately correct
    count = start_count
    data_errors = []  # Items with malformed Unicode

    prev = None
    index = 0
    line_number = 0
    for item in raw_testdata_list[1:]:

        line_number += 1
        if recommentline.match(item) or reblankline.match(item):
            continue
        # It's a data line.
        if not prev:
            # Just getting started.
            prev = parseCollTestData(item)
            continue

        # Get the code points for each test
        next = parseCollTestData(item)

        if not next:
            # This is a problem with the data input. D80[0-F] is the high surrogate
            data_errors.append([index, item])
            continue

        label = str(count).rjust(max_digits, '0')
        new_test = {'label': label, 's1': prev, 's2': next, 'line': line_number}
        if ignorePunctuation:
            new_test['ignorePunctuation'] = True
        test_list.append(new_test)

        verify_list.append({'label': label, 'verify': True})

        prev = next  # set up for next pair
        count += 1
        index += 1

    logging.info('Coll Test: %d lines processed', len(test_list))
    if data_errors:
        logging.warning('!! %s File %s has DATA ERRORS: %s',
                        filename, len(data_errors), data_errors)

    return test_list, verify_list


def insert_collation_header(test_objs):
    for obj in test_objs:
        obj['Test scenario'] = 'collation_short'
        obj['description'] =  'UCA conformance test. Compare the first data string with the second and with strength = identical level (using S3.10). If the second string is greater than the first string, then stop with an error.'


def insert_nonignorable_coll_descr(tests_obj, verify_obj):
  verify_obj['Test Scenario'] = tests_obj['Test scenario'] = "coll_nonignorable_short"
  tests_obj['description'] =  'UCA conformance test. Compare the first data string with the second and with strength = identical level (using S3.10). If the second string is greater than the first string, then stop with an error.'
  return


def languageNameDescr(tests_json, verify_json):
    # Adds information to LanguageName tests and verify JSON
    descr =  'Language display name test cases. The first code declares the language whose display name is requested while the second code declares the locale to display the language name in.'
    test_id =  'lang_names'
    source_url = 'No URL yet.'
    version = 'unspecified'
    tests_json = {
        'test_type': test_id,
        'Test scenario': test_id,
        'description': descr,
        'source': {
            'repository': 'conformance-test',
            'version': 'trunk',
            'url': source_url,
            'source_version': version
        }
    }

    verify_json = {'test_type': test_id,
                   'Test scenario': test_id
                   }
    return


def insertNumberFmtDescr(tests_obj, verify_obj):
  # returns JSON data for tests and verification
  test_scenario = 'number_fmt'
  test_data = {
      'Test scenario': test_scenario,
      'test_type': 'number_fmt',
      'description':
          'Number formatter test cases. The skeleton entry corresponds to the formatting specification used by ICU while the option entries adhere to ECMA-402 syntax.',
      "source": {"repository": "icu", "version": "trunk"},
      "url": "https://raw.githubusercontent.com/unicode-org/icu/main/icu4c/source/test/testdata/numberpermutationtest.txt",
      'tests': tests_obj
  }
  verify_data = {
      'Test scenario': test_scenario,
      'test_type': 'number_fmt',
      'verifications': verify_obj
  }
  return test_data, verify_data


def setupArgs():
    parser = argparse.ArgumentParser(prog='testdata_gen')
    parser.add_argument('--icu_versions', nargs='*', default=[])
    # -1 is no limit
    parser.add_argument('--run_limit', nargs='?', type=int, default=-1)
    new_args = parser.parse_args()
    return new_args


def main(args):
    new_args = setupArgs()

    logger = logging.Logger("TEST_GENERATE LOGGER")
    logger.setLevel(logging.INFO)
    logger.info('+++ Generating .json files for icu_versions %s',
                 new_args.icu_versions)

    for icu_version in new_args.icu_versions:
        data_generator = generateData(icu_version)
        data_generator.run_limit = new_args.run_limit

        # TODO: Why doesn't logging.info produce output?
        logging.info('Generating .json files for data driven testing. ICU_VERSION requested = %s',
                     icu_version)

        data_generator.processNumberFmtTestData()

        # This is slow
        data_generator.processCollationTestData()

        data_generator.processLikelySubtagsData()

        # This is slow
        data_generator.processLangNameTestData()

        logger.info('++++ Data generation for %s is complete.', icu_version)


if __name__ == '__main__':
  main(sys.argv)
