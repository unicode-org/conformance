# -*- coding: utf-8 -*-

import argparse
import json
import logging
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

    def setVersion(self, selected_version):
        self.icu_version = selected_version

    def saveJsonFile(self, filename, data, indent=None):
      output_path = os.path.join(self.icu_version, filename)
      output_file = open(output_path, 'w')
      json.dump(data, output_file, indent=1)
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
      # Alternate set of data, not used right now.
      #rawtestdata = readFile('CollationTest_NON_IGNORABLE_SHORT.txt')

      # Read raw data
      filename = 'CollationTest_SHIFTED_SHORT.txt'

      rawcolltestdata = readFile(filename, self.icu_version)

      if not rawcolltestdata:
          return None

      test_list = rawcolltestdata.splitlines()
      # test_list = rawcolltestdata.splitlines()  #OLD

      # Get lists of tests and verify info
      testdata_object_list, verify_list = generateCollTestDataObjects(test_list)
      json_test = {}
      json_verify = {}
      insert_coll_descr(json_test, json_verify)
      json_verify['verifications'] = verify_list
      json_test['tests'] = testdata_object_list

      # And write the files
      self.saveJsonFile('coll_test_shift.json', json_test)
      self.saveJsonFile('coll_verify_shift.json', json_verify)

      return True

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

            self.saveJsonFile('num_fmt_test_file.json', json_test)

            output_path = os.path.join(self.icu_version, 'num_fmt_verify_file.json')
            num_fmt_verify_file = open(output_path, 'w')
            json.dump(json_verify, num_fmt_verify_file, indent=1)
            num_fmt_verify_file.close()

            logging.warning('NumberFormat Test (%s): %s tests created', self.icu_version, count)
        return

    def processLangNameTestData(self):

        json_test = {}
        json_verify = {}
        languageNameDescr(json_test, json_verify)
        filename = 'languageNameTable.txt'
        rawlangnametestdata = readFile(filename, self.icu_version)

        if not rawlangnametestdata:
            return None

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

      json_tests['tests'] = jtests
      json_verify['verifications'] = jverify

      logging.info('LangNames Test (%s): %d lines processed', self.icu_version, count)
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
      "unit-width-narrow": {"unitDisplay": "narrow", "currencyDisplay": "symbol"},
      "unit-width-full-name": {"unitDisplay": "long", "currencyDisplay": "name"},
      #"unit-width-full-name": {"unitDisplay": "long"},
      "precision-integer": {"maximumFractionDigits": "0", "minimumFractionDigits": "0", "roundingType": "fractionDigits"},
      ".000": {"maximumFractionDigits": "3", "minimumFractionDigits": "3"},

      # Use maximumFractionDigits: 2, maximumSignificantDigits: 3, roundingPriority: "morePrecision"
      ".##/@@@+": {"maximumFractionDigits": "2", "maximumSignificantDigits": "3","roundingPriority": "morePrecision"},
      "@@": {"maximumSignificantDigits": "2", "minimumSignificantDigits": "2"},
      "rounding-mode-floor": {"roundingMode": "floor"},
      "integer-width/##00": {"maximumIntegerDigits": "4", "minimumIntegerDigits":"2"},
      "group-on-aligned": {"useGrouping": "true"},
      "latin": {"numberingSystem": "latn"},
      "sign-accounting-except-zero": {"signDisplay": "exceptZero"},
      "0.0000E0": {"notation": "scientific", "minimumIntegerDigits": "1", "minimumFractionDigits": "4", "maximumFractionDigits": "4"},
      "00": {"minimumIntegerDigits":"2"},
      "#.#": {"maximumFractionDigits": "1"},
      "@@@": {"minimumSignificantDigits": "3", "maximumSignificantDigits": "3"},
      "@@###": {"minimumSignificantDigits": "2", "maximumSignificantDigits": "5"},
      "@@@@E0": {"notation": "scientific", "minimumSignificantDigits": "4", "maximumSignificantDigits": "4"},
      "0.0##E0": {"notation": "scientific", "minimumIntegerDigits":"1", "minimumFractionDigits": "1", "maximumFractionDigits": "3"},
      "00.##E0": {"notation": "scientific", "minimumIntegerDigits":"2", "minimumFractionDigits": "1", "maximumFractionDigits": "3"},
      "0005": {"minimumIntegerDigits":"2"},
      "0.00": {"minimumIntegerDigits":"1", "minimumFractionDigits": "2", "maximumFractionDigits": "2"},
      "0.000E0": {"notation": "scientific", "minimumIntegerDigits":"1", "minimumFractionDigits": "3", "maximumFractionDigits": "3"},
      "0.0##": {"minimumIntegerDigits":"1", "minimumFractionDigits": "1", "maximumFractionDigits": "3"},
      "#": {"minimumIntegerDigits":"1", "maximumFractionDigits": "0"},
      "0.#E0": {"notation": "scientific", "minimumIntegerDigits":"1", "maximumFractionDigits": "1"},
      "0.##E0": {"notation": "scientific", "minimumIntegerDigits":"1", "maximumFractionDigits": "2"},
      ".0E0": {"notation": "scientific", "minimumIntegerDigits":"0", "minimumFractionDigits": "1", "maximumFractionDigits": "1"},
      ".0#E0": {"notation": "scientific", "minimumIntegerDigits":"0", "minimumFractionDigits": "1", "maximumFractionDigits": "2"},
      "@@@@@@@@@@@@@@@@@@@@@@@@@": {"minimumSignificantDigits": "25", "maximumSignificantDigits": "25"},
      "0.0": {"minimumIntegerDigits":"1", "minimumFractionDigits": "2", "maximumFractionDigits": "2"}
      }

  ecma402_options = []

  options_dict = {}
  # Which combinatins of skeleton entries need modificiation?
  # Look at the expected output...
  for o in options:
    if o != 'scale/0.5' and o != 'decimal-always':
      option_detail = ecma402_map[o]
      options_dict = options_dict | option_detail

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
      "ceiling": 'ceiling',
      "unnecessary": 'none'
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
  # TODO: fix
  resolved = raw_options
  if 'minimumSignificantDigits' in resolved and 'maximumFractionDigits' in resolved:
    resolved.pop('minimumSignificantDigits')

  if skeleton_list and 'percent' in skeleton_list:
    resolved['style'] = 'unit'
    resolved['unit'] = 'percent'
    if 'unit-width-full-name' in skeleton_list:
        resolved['currencyDisplay'] = 'name'
        resolved['unitDisplay'] = 'long'
  return resolved


# Count is the starting point for the values
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
      entry = {'label': label, 'op': 'format', 'skeleton': pattern , 'input': test_input, 'options': {} }

      json_part = mapFmtSkeletonToECMA402([pattern])

      resolved_options_dict = resolveOptions(json_part, None)

      if not json_part:
          x = 1
      if rounding_mode:
          entry['options']['roundingMode'] = rounding_mode
      entry['options'] |= json_part

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
        teststring = chr(cp)
    return teststring


def generateCollTestDataObjects(testdata_list):
  recommentline = re.compile('^\s*#')

  test_list = []
  verify_list = []

  max_digits = computeMaxDigitsForCount(len(testdata_list))  # Approximately correct
  count = 0
  data_errors = []  # Items with malformed Unicode

  prev = None
  for item in testdata_list[1:]:
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
          data_errors.append(item)
          continue
      label = str(count).rjust(max_digits, '0')
      test_list.append({'label': label, 'string1': prev, 'string2': next})
      verify_list.append({'label': label, 'verify': True})

      prev = next  # set up for next pair
      count += 1

  logging.info('Coll Test: %d lines processed', len(test_list))
  if data_errors:
      logging.info('!! %s DATA ERRORS: %s', len(data_errors), data_errors)
  return test_list, verify_list


def insert_coll_descr(tests_obj, verify_obj):
  verify_obj['Test Scenario'] = tests_obj['Test scenario'] = "coll_shift_short"
  tests_obj['description'] =  'UCA conformance test. Compare the first data string with the second and with strength = identical level (using S3.10). If the second string is greater than the first string, then stop with an error.'
  return


def languageNameDescr(tests_json, verify_json):
  # Adds information to LanguageName tests and verify JSON
  descr =  'Language display name test cases. The first code declares the language whose display name is requested while the second code declares the locale to display the language name in.'
  test_id =  'language_display_name'
  version = {'source': {'repository': 'conformance-test', 'version': 'trunk'}}
  source = 'No URL yet.'
  tests_json['Test scenario'] = test_id
  tests_json['description'] = descr
  tests_json['version'] = version
  tests_json['url'] = source
  verify_json['Test scenario'] = test_id

  return


def insertNumberFmtDescr(tests_obj, verify_obj):
  # returns JSON data for tests and verification
  test_scenario = 'number_fmt'
  test_data = {
      "Test scenario": test_scenario,
      'description':
          'Number formatter test cases. The skeleton entry corresponds to the formatting specification used by ICU while the option entries adhere to ECMA-402 syntax.',
      "source": {"repository": "icu", "version": "trunk"},
      "url": "https://raw.githubusercontent.com/unicode-org/icu/main/icu4c/source/test/testdata/numberpermutationtest.txt",
      'tests': tests_obj
  }
  verify_data = {
      "Test scenario": test_scenario, 'verifications': verify_obj
  }
  return test_data, verify_data


def setupArgs():
    parser = argparse.ArgumentParser(prog='testdata_gen')
    parser.add_argument('--icu_versions', nargs='*', default=[])
    new_args = parser.parse_args()
    return new_args


def main(args):
    new_args = setupArgs()

    logger = logging.Logger("TEST_GENEREATE LOGGER")
    logger.setLevel(logging.INFO)
    logger.info('+++ Generating .json files for icu_versions %s',
                 new_args.icu_versions)

    for icu_version in new_args.icu_versions:
        data_generator = generateData(icu_version)

        # TODO: WHy doesn't logging.info produce output?
        logging.info('Generating .json files for data driven testing. ICU_VERSION requested = %s',
                     icu_version)

        data_generator.processCollationTestData()

        data_generator.processNumberFmtTestData()
        data_generator.processLangNameTestData()

        logger.info('++++ Data generation for %s is complete.', icu_version)


if __name__ == '__main__':
  main(sys.argv)
