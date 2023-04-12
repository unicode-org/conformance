# -*- coding: utf-8 -*-

import json
import os
import re
import sys

reblankline = re.compile('^\s*$')

def readFile(filename):
  with open(filename, 'r', encoding='utf8') as testdata:
    return testdata.read()

def insertJObj(object_list, depth):
  indent = '\n'.ljust(depth+1, ' ')
  blanks = ''.ljust(depth, ' ')

  for i in range(0, len(object_list)):
    if not reblankline.match(object_list[i]):
      object_list[i] = blanks + object_list[i].replace('\n', indent)

  return object_list

def parseCollTestData(testdata):
  recodepoint = re.compile(r'[0-9a-fA-F]{4,6}')

  codepoints = recodepoint.findall(testdata)
  return codepoints

def parseDcmlFmtTestData(rawtestdata):
  reformat = re.compile(r'format +([\d.E@\#]+) +(default|ceiling|floor|down|up|halfeven|halfdown|halfup|unnecessary) +\"(-?[\d.E]+)\" +\"(-?[\d.E]+|Inexact)\"')

  test_match = reformat.search(rawtestdata)
  return test_match.group(1), test_match.group(2), test_match.group(3), test_match.group(4)

def mapFmtSkeletonToECMA402(options):
  ecma402_map = {
      "compact-short": {"notation": "compact",  "compactDisplay": "short"},
      "scientific/+ee/sign-always": {"notation": "scientific"},
      # Percent with word "percent":
      "percent": {"style": "unit", "unit": "percent"},  # "style": "percent",
      "currency/EUR": {"style": "currency", "currencyDisplay": "symbol",  "currency": "EUR"},
      "measure-unit/length-meter": {"style": "unit",  "unit": "meter"},
      #"measure-unit/length-furlong": {"style": "unit", "unit": "furlong"},
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


def generateLanguageNameTestDataObjects(rawtestdata, json_tests, json_verify):
  # Get the JSON data for tests and verification for language names
  recommentline = re.compile('^\s*#')
  count = 0

  jtests = []
  jverify = []

  for item in rawtestdata.splitlines():
    if not (recommentline.match(item) or reblankline.match(item)):
      test_data = parseLanguageNameData(item)
      if test_data == None:
        print('  LanguageNames: Line \'%s\' not recognized as valid test data entry' % item)
        continue
      else:
        label = str(count).rjust(7, '0')
        test_json = {'label': label, 'language_label': test_data[0], 'locale_label': test_data[1]}
        jtests.append(test_json)
        jverify.append({'label': label, 'verify': test_data[2]})
        count += 1

  json_tests['tests'] = jtests
  json_verify['verifications'] = jverify

  print('LangNames Test: %d lines processed' % count)
  return

def generateNumberFmtTestDataObjects(rawtestdata, count=0):
  # Returns 2 lists JSON-formatted: all_tests_list, verify_list
  entry_types = {
      "compact-short": "notation",
      "scientific/+ee/sign-always": "notation",
      "percent": "unit",
      "currency/EUR": "unit",  ## TODO: Change the unit
      "measure-unit/length-meter": "unit",
      #"measure-unit/length-furlong": "unit",
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
  numbers_to_test = ['0', '91827.3645', '-0.22222']
  test_list = parseNumberFmtTestData(rawtestdata)
  ecma402_options_start = ['"options": {\n']

  all_tests_list = []
  verify_list = []
  for t in test_list:
    # The first three specify the formatting.
    # Example: compact-short percent unit-width-full-name
    part1 = entry_types[t[0]]
    part2 = entry_types[t[1]]
    part3 = entry_types[t[2]]

    # TODO: use combinations of part1, part2, and part3 to generate options.
    # Locales are in element 3, 7, and 11 of parsed structure.

    for l in { 3, 7, 11 }:
      for n in range(len(numbers_to_test)):
        ecma402_options = []
        label = str(count).rjust(7, '0')
        expected = t[l + 1 + n]
        verify_json = {'label': label, 'verify': expected}
        verify_list.append(verify_json)

        # TODO: Use JSON module instead of print formatting
        skeleton = '%s %s %s' % (t[0], t[1], t[2])
        entry = {'label': str(count).rjust(7, '0'),
                 'locale': t[l],
                 'skeleton': skeleton,
                 'input': numbers_to_test[n]
                 }

        options_dict = mapFmtSkeletonToECMA402([t[0], t[1], t[2]])
        if not options_dict:
            print(
                '$$$ OPTIONS not found for %s' % label
            )
        # TODO: Look at the items in the options_dict to resolve conflicts and set up things better.
        resolved_options_dict = resolveOptions(options_dict, t)
        # include these options in the entry
        entry = entry | {'options': resolved_options_dict}

        all_tests_list.append(entry)  # All the tests in JSON form
        count += 1

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

def generateDcmlFmtTestDataObjects(rawtestdata, count=0):
  recommentline = re.compile('^\s*#')
  test_list = rawtestdata.splitlines()

  all_tests_list = []
  verify_list = []
  for item in test_list[1:]:
    if not (recommentline.match(item) or reblankline.match(item)):
      pattern, round_mode, test_input, expected = parseDcmlFmtTestData(item)
      rounding_mode = mapRoundingToECMA402(round_mode)
      label = str(count).rjust(7, '0')
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

  return all_tests_list, verify_list, count


def generateCollTestDataObjects(testdata_list):
  recommentline = re.compile('^\s*#')

  n = 0
  colltestdata = []
  for item in testdata_list:
    if not (recommentline.match(item) or reblankline.match(item)):
      # Get the code points for each test
      codepoints = parseCollTestData(item)
      testdatastring = ''
      for cp in codepoints:
        if int('0x' + cp, 16) < 32 or int('0x' + cp, 16) == 127:
          testdatastring = testdatastring + '\\u' + cp
        elif cp == '0022':
          # print('Double quote encountered')
          testdatastring = testdatastring +'\\"'
        elif cp == '005C':
          testdatastring = testdatastring +'\\\\'
        else:
          testdatastring = testdatastring + chr(int('0x' + cp, 16))

      colltestdata.append(testdatastring)
      n += 1

  print('Coll Test: %d lines processed' % n)

  # Construct test data and verification entries in JSON.
  count = 0
  prev = colltestdata[0]
  test_list = []
  verify_list = []
  for t in colltestdata[1:]:
    label = str(count).rjust(7, '0')
    test_list.append({'label': label, 'string1': prev, 'string2': t})
    verify_list.append({'label': label, 'verify': True})
    prev = t
    count += 1

  # Special op: remove ',' from end of last list entry.
  # TODO: Clean up old string types
  return test_list, verify_list  # testdata_jobjs, verify_jobjs

def generateTestsObject(testdata_object_list):
  #tests_begin = '"tests": ['
  #tests_end = ']'

  #tests_jobj = [tests_begin] + insertJObj(testdata_object_list, 2) + [tests_end]
  return {'tests': testdata_object_list}

def generateVerifyObject(verification_object_list):
  return {'verifications': verification_object_list}

def insert_coll_descr(tests_obj, verify_obj):
  verify_obj['Test Scenario'] = tests_obj['Test scenario'] = "coll_shift_short"
  tests_obj['description'] =  'UCA conformance test. Compare the first data string with the second and with strength = identical level (using S3.10). If the second string is greater than the first string, then stop with an error.'
  return

def processCollationTestData():
  # Alternate set of data, not used right now.
  #rawtestdata = readFile('CollationTest_NON_IGNORABLE_SHORT.txt')

  # Read raw data
  rawcolltestdata = readFile('CollationTest_SHIFTED_SHORT.txt')

  test_list = rawcolltestdata.splitlines()

  # Get lists of tests and verify info
  testdata_object_list, verify_list = generateCollTestDataObjects(test_list)
  json_test = {}
  json_verify = {}
  insert_coll_descr(json_test, json_verify)
  json_verify['verifications'] = verify_list
  json_test['tests'] = testdata_object_list

  # And write the files
  coll_test_file = open('coll_test_shift.json', 'w')
  json.dump(json_test, coll_test_file, indent=1)
  coll_test_file.close()

  coll_verify_file = open('coll_verify_shift.json', 'w')
  # The verify file doesn't need to be pretty-printed
  json.dump(json_verify, coll_verify_file, indent=1)
  coll_verify_file.close()

  return

def insert_decml_fmt_descr(tests_obj, verify_obj):
  icu_tag = 'maint-71'
  source_url = "http://raw.githubusercontent.com/unicode-org/icu/maint/%s/icu4c/source/test/testdata/dcfmtest.txt" % (icu-tag)
  descr =   ('{\n'
             '  "description": "Decimal formatter test cases for parsing and formatting.\\n'
             '  Formatting test case elements:\\n'
             '  format  pattern round-mode decimal-number\\n'
             '  Parse test case elements:\\n'
             '  parse input-text type",')
  test_id =  '  "Test scenario": "decimal_fmt",'
  version = ('  "source":\n'
             '    {\n'
             '      "repository": "icu",\n'
             '      "version": "trunk"\n'
             '    },')
  source =   '  "url": "%s,"' % source_url
#  source =   '  "url": "http://raw.githubusercontent.com/unicode-org/icu/maint/maint-71/icu4c/source/test/testdata/dcfmtest.txt",'
  end = '}'
  verify_head = '{\n  "Test scenario": "decimal_fmt",'

  return [descr] + [test_id] + [version] + [source] + insertJObj(tests_obj, 2) + [end], [verify_head] + insertJObj(verify_obj, 2) + [end]

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

  return


def processDcmlFmtTestDataObjects(rawtestdata):
  testdata_object_list, verify_object_list, count = generateDcmlFmtTestDataObjects(rawtestdata, 0)
  json_test = {}
  json_verify = {}
  json_test['tests'] = generateTestsObject(testdata_object_list)
  json_verify['verification'] = generateVerifyObject(verify_object_list)
  insert_decml_fmt_descr(json_test, json_verify)

  return json_test, verify

def processNumberFmtTestData():
  rawdcmlfmttestdata = readFile('dcfmtest.txt')
  BOM = '\xef\xbb\xbf'
  if rawdcmlfmttestdata.startswith(BOM):
    print('Skip BOM')
    rawdcmlfmttestdata = rawdcmlfmttestdata[3:]
  #dcml_fmt_test, dcml_fmt_verify = processDcmlFmtTestDataObjects(rawdcmlfmttestdata)
  #dcml_fmt_test_file = open('dcml_fmt_test_file.json', 'w')
  #for t in dcml_fmt_test:
  #   dcml_fmt_test_file.write(t)
  #   dcml_fmt_test_file.write('\n')
  #dcml_fmt_test_file.close()

  #dcml_fmt_verify_file = open('dcml_fmt_verify.json', 'w')
  #for v in dcml_fmt_verify:
  #  dcml_fmt_verify_file.write(v)
  #  dcml_fmt_verify_file.write('\n')
  #dcml_fmt_verify_file.close()
  # Get the raw string data
  rawnumfmttestdata = readFile('numberpermutationtest.txt')

  num_testdata_object_list, num_verify_object_list, count = generateNumberFmtTestDataObjects(rawnumfmttestdata)
  dcml_testdata_object_list, dcml_verify_object_list, count = generateDcmlFmtTestDataObjects(rawdcmlfmttestdata, count)

  test_list = num_testdata_object_list + dcml_testdata_object_list
  verify_list = num_verify_object_list + dcml_verify_object_list
  json_test, json_verify = insertNumberFmtDescr(test_list, verify_list)

  num_fmt_test_file = open('num_fmt_test_file.json', 'w')
  json.dump(json_test, num_fmt_test_file, indent=1)
  num_fmt_test_file.close()

  num_fmt_verify_file = open('num_fmt_verify_file.json', 'w')
  json.dump(json_verify, num_fmt_verify_file, indent=1)
  num_fmt_verify_file.close()

  print('NumberFormat Test: %s tests created' % count)
  return


def processLangNameTestData():

    json_test = {}
    json_verify = {}
    languageNameDescr(json_test, json_verify)
    rawlangnametestdata = readFile('languageNameTable.txt')

    generateLanguageNameTestDataObjects(
        rawlangnametestdata, json_test, json_verify)

    lang_name_test_file = open('lang_name_test_file.json', 'w')
    json.dump(json_test, lang_name_test_file, indent=1)
    lang_name_test_file.close()

    lang_name_verify_file = open('lang_name_verify_file.json', 'w')
    json.dump(json_verify, lang_name_verify_file, indent=1)
    lang_name_verify_file.close()

    return


def main():
  print('Generating .json files for data driven testing')

  processNumberFmtTestData()
  processLangNameTestData()

  processCollationTestData()

  print('================================================================================')


if __name__ == '__main__':
  main()
