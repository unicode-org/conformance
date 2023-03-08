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
      "compact-short": '"notation": "compact",\n  "compactDisplay": "short",\n',
      "scientific/+ee/sign-always": '"notation": "scientific",\n',
      # Percent with word "percent":
      #    {'style': 'unit', unit:'percent', 'unitDisplay': 'long'})

      "percent": '"style": "percent",\n',
      # "currency/EUR": '"style": "currency",\n  "currencyDisplay": "code",\n  "code": "EUR",\n',
      "currency/EUR": '"style": "currency",\n  "currencyDisplay": "symbol",\n  "code": "EUR",\n',
      "measure-unit/length-meter": '"style": "unit",\n  "unit": "meter",\n',
      # "measure-unit/length-furlong": '"style": "unit",\n  "unit": "furlong",\n',
      "unit-width-narrow": '"unitDisplay": "narrow",\n',
      "unit-width-full-name": '"unitDisplay": "long", "currencyDisplay":"name", \n',
      #"unit-width-full-name": '"unitDisplay": "long",\n',
      "precision-integer": '"maximumFractionDigits": "0",\n  "minimumFractionDigits": "0",\n  "roundingType": "fractionDigits",\n',
      ".000": '"maximumFractionDigits": "3",\n  "minimumFractionDigits": "3",\n',
      ".##/@@@+": '"maximumFractionDigits": "2",\n  "minimumSignificantDigits": "3",\n',
      "@@": '"maximumSignificantDigits": "2",\n  "minimumSignificantDigits": "2",\n',
      "rounding-mode-floor": '"roundingMode": "floor",\n',
      "integer-width/##00": '"maximumIntegerDigits": "4",\n  "minimumIntegerDigits":"2",\n',
      "group-on-aligned": '"useGrouping": "true",\n',
      "latin": '"numberingSystem": "latn",\n',
      "sign-accounting-except-zero": '"signDisplay": "exceptZero",\n',
      "0.0000E0": '"notation": "scientific",\n  "minimumIntegerDigits": "1",\n  "minimumFractionDigits": "4",\n  "maximumFractionDigits": "4",\n',
      "00": '"minimumIntegerDigits":"2",\n',
      "#.#": '"maximumFractionDigits": "1",\n',
      "@@@": '"minimumSignificantDigits": "3",\n  "maximumSignificantDigits": "3",\n',
      "@@###": '"minimumSignificantDigits": "2",\n  "maximumSignificantDigits": "5",\n',
      "@@@@E0": '"notation": "scientific",\n  "minimumSignificantDigits": "4",\n  "maximumSignificantDigits": "4",\n',
      "0.0##E0": '"notation": "scientific",\n  "minimumIntegerDigits":"1",\n  "minimumFractionDigits": "1",\n  "maximumFractionDigits": "3",\n',
      "00.##E0": '"notation": "scientific",\n  "minimumIntegerDigits":"2",\n  "minimumFractionDigits": "1",\n  "maximumFractionDigits": "3",\n',
      "0005": '"minimumIntegerDigits":"2",\n',
      "0.00": '"minimumIntegerDigits":"1",\n  "minimumFractionDigits": "2",\n  "maximumFractionDigits": "2",\n',
      "0.000E0": '"notation": "scientific",\n  "minimumIntegerDigits":"1",\n  "minimumFractionDigits": "3",\n  "maximumFractionDigits": "3",\n',
      "0.0##": '"minimumIntegerDigits":"1",\n  "minimumFractionDigits": "1",\n  "maximumFractionDigits": "3",\n',
      "#": '"minimumIntegerDigits":"1",\n  "maximumFractionDigits": "0",\n',
      "0.#E0": '"notation": "scientific",\n  "minimumIntegerDigits":"1",\n  "maximumFractionDigits": "1",\n',
      "0.##E0": '"notation": "scientific",\n  "minimumIntegerDigits":"1",\n  "maximumFractionDigits": "2",\n',
      ".0E0": '"notation": "scientific",\n  "minimumIntegerDigits":"0",\n  "minimumFractionDigits": "1",\n  "maximumFractionDigits": "1",\n',
      ".0#E0": '"notation": "scientific",\n  "minimumIntegerDigits":"0",\n  "minimumFractionDigits": "1",\n  "maximumFractionDigits": "2",\n',
      "@@@@@@@@@@@@@@@@@@@@@@@@@": '"minimumSignificantDigits": "25",\n  "maximumSignificantDigits": "25",\n',
      "0.0": '"minimumIntegerDigits":"1",\n  "minimumFractionDigits": "2",\n  "maximumFractionDigits": "2",\n'
      }

  ecma402_options = []

  # Which combinatins of skeleton entries need modificiation?
  # Look at the expected output...
  for o in options:
    if o != 'scale/0.5' and o != 'decimal-always':
      ecma402_options.append(ecma402_map[o])
   # TODO: resolve some combinations of entries that are in conflict
  # Remove comma after last entry, add closing bracket.
  #(start, comma, end) = ecma402_options[-1].rpartition(',')
  #ecma402_options[-1] = start + '\n},' + end

  return ecma402_options

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


def generateLanguageNameTestDataObjects(rawtestdata):
  recommentline = re.compile('^\s*#')
  test_list = rawtestdata.splitlines()
  count = 0
  testdata_jobjs = []
  verifydata_jobjs = []

  for item in test_list:
    # if recommentline.match(item):
    #   print('Comment line')
    if not (recommentline.match(item) or reblankline.match(item)):
      test_data = parseLanguageNameData(item)
      if test_data == None:
        print('  LanguageNames: Line \'%s\' not recognized as valid test data entry' % item)
        continue
      else:
        test_data_entry = '{\n  "label": "%s",\n  "language_label": "%s",\n  "locale_label": "%s"\n},' % (str(count).rjust(7, '0'), test_data[0], test_data[1])
        testdata_jobjs.append(test_data_entry)
        verifydata = '{\n  "label": "%s",\n  "verify": "%s"\n},' % (str(count).rjust(7, '0'), test_data[2])
        verifydata_jobjs.append(verifydata)
        count += 1

  # Special op: remove ',' from end of last list entry.
  testdata_jobjs[-1] = testdata_jobjs[-1].rstrip(',')
  verifydata_jobjs[-1] = verifydata_jobjs[-1].rstrip(',')

  print('LangNames Test: %d lines processed' % count)
  return testdata_jobjs, verifydata_jobjs

def generateNumberFmtTestDataObjects(rawtestdata):
  entry_types = {
      "compact-short": "notation",
      "scientific/+ee/sign-always": "notation",
      "percent": "unit",
      "currency/EUR": "unit",
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
  count = 0
  testdata_jobjs = []
  verifydata_jobjs = []
  ecma402_options_start = ['"options": {\n']

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

        verifydata = '{\n  "label": "%s",\n  "verify": "%s"\n},' % (str(count).rjust(7, '0'), t[l + 1 + n])
        verifydata_jobjs.append(verifydata)

        entry_top = '{\n  "label": "%s",\n  "locale": "%s",\n  "skeleton": "%s %s %s",\n' % (str(count).rjust(7, '0'), t[l], t[0], t[1], t[2])
        entry_bottom = '"input": "%s"\n},' % numbers_to_test[n]
        ecma402_options_body = mapFmtSkeletonToECMA402([t[0], t[1], t[2]])
        # Remove comma after last entry, add closing bracket.
        (start, comma, end) = ecma402_options_body[-1].rpartition(',')
        ecma402_options_body[-1] = start + '\n},' + end
        ecma402_options = ecma402_options_start +  ecma402_options_body   # mapFmtSkeletonToECMA402([t[0], t[1], t[2]])
        ecma402_jobj = ''.join(ecma402_options)
        ecma402_entry = [entry_top] + insertJObj(ecma402_options, 2) + [entry_bottom]
        testdata_jobjs.append(''.join(ecma402_entry))
        count += 1

  # Special op: remove ',' from end of last list entry.
  #testdata_jobjs[-1] = testdata_jobjs[-1].rstrip(',')
  #verifydata_jobjs[-1] = verifydata_jobjs[-1].rstrip(',')

  return testdata_jobjs, verifydata_jobjs, count

def generateDcmlFmtTestDataObjects(rawtestdata, count):
  recommentline = re.compile('^\s*#')
  test_list = rawtestdata.splitlines()
  # count = 0
  testdata_jobjs = []
  verifydata_jobjs = []

  for item in test_list[1:]:
    if not (recommentline.match(item) or reblankline.match(item)):
      pattern, round_mode, test_input, expected = parseDcmlFmtTestData(item)
      rounding =  '"roundingMode": "%s",\n' % mapRoundingToECMA402(round_mode)
      entry_top = '{\n  "label": "%s",\n  "op": "format",\n  "skeleton": "%s",\n' % (str(count).rjust(7, '0'), pattern)
      entry_bottom = '"input": "%s"\n},' % test_input
      ecma402_options_body = mapFmtSkeletonToECMA402([pattern]) + [rounding]
      # Remove comma after last entry, add closing bracket.
      (start, comma, end) = ecma402_options_body[-1].rpartition(',')
      ecma402_options_body[-1] = start + '\n},' + end
      ecma402_options = ['"options": {\n'] + ecma402_options_body   # mapFmtSkeletonToECMA402([pattern]) + [rounding]

      ecma402_jobj = ''.join(ecma402_options)
      ecma402_entry = [entry_top] + insertJObj(ecma402_options, 2) + [entry_bottom]
      testdata_jobjs.append(''.join(ecma402_entry))
      verifydata = '{\n  "label": "%s",\n  "verify": "%s"\n},' % (str(count).rjust(7, '0'), expected)
      verifydata_jobjs.append(verifydata)
      count += 1

  # Special op: remove ',' from end of last list entry.
  testdata_jobjs[-1] = testdata_jobjs[-1].rstrip(',')
  verifydata_jobjs[-1] = verifydata_jobjs[-1].rstrip(',')

  print('DcmlFmt Test: %d lines processed' % count)
  return testdata_jobjs, verifydata_jobjs

def generateCollTestDataObjects(testdata_list):
  recommentline = re.compile('^\s*#')

  n = 0
  colltestdata = []
  for item in testdata_list:
    if not (recommentline.match(item) or reblankline.match(item)):
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
  testdata_jobjs = []
  verify_jobjs = []
  count = 0
  prev = colltestdata[0]
  for t in colltestdata[1:]:
    entry = '{\n  "label": "%s",\n  "string1": "%s",\n  "string2": "%s"\n},' % (str(count).rjust(7, '0'), prev, t)
    testdata_jobjs.append(entry)
    verify = '{\n  "label": "%s",\n  "verify": "True"\n},' % (str(count).rjust(7, '0'))
    verify_jobjs.append(verify)
    prev = t
    count += 1

  # Special op: remove ',' from end of last list entry.
  testdata_jobjs[-1] = testdata_jobjs[-1].rstrip(',')
  verify_jobjs[-1] = verify_jobjs[-1].rstrip(',')

  return testdata_jobjs, verify_jobjs

def generateTestsObject(testdata_object_list):
  tests_begin = '"tests": ['
  tests_end = ']'

  tests_jobj = [tests_begin] + insertJObj(testdata_object_list, 2) + [tests_end]
  return tests_jobj

def generateVerifyObject(verification_object_list):
  verify_begin = '"verifications": ['
  verify_end = ']'

  verify_jobj = [verify_begin] + insertJObj(verification_object_list, 2) + [verify_end]
  return verify_jobj

def insert_coll_descr(tests_obj, verify_obj):
  descr =   ('{\n'
             '  "description": "UCA conformance test. Compare the first data\\n'
             '   string with the second and with strength = identical level\\n'
             '   (using S3.10). If the second string is greater than the first\\n'
             '   string, then stop with an error.",')
  test_id =  '  "Test scenario": "coll_shift_short",'
  end = '}'

  verify_head = '{\n  "Test scenario": "coll_shift_short",'

  return [descr] + [test_id] + insertJObj(tests_obj, 2) + [end], [verify_head] + insertJObj(verify_obj, 2) + [end]

def processTestData(rawtestdata):
  test_list = rawtestdata.splitlines()
  testdata_object_list, verify_list = generateCollTestDataObjects(test_list)
  verify_object = generateVerifyObject(verify_list)
  tests_object = generateTestsObject(testdata_object_list)
  json_test, json_verify = insert_coll_descr(tests_object, verify_object)
  #for t in json_test:
  #  print(t)

  return json_test, json_verify

def insert_descr(tests_obj, verify_obj):
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
  source =   '  "url": "http://raw.githubusercontent.com/unicode-org/icu/maint/maint-71/icu4c/source/test/testdata/dcfmtest.txt",'
  end = '}'
  verify_head = '{\n  "Test scenario": "decimal_fmt",'

  return [descr] + [test_id] + [version] + [source] + insertJObj(tests_obj, 2) + [end], [verify_head] + insertJObj(verify_obj, 2) + [end]

def languageNameDescr(tests_obj, verify_obj):
  descr =   ('{\n'
             '  "description": "Language display name test cases. The first\\n'
             '  code declares the language whose display name is requested\\n'
             '  while the second code declares the locale to display the\\n'
             '  language name in.",')
  test_id =  '  "Test scenario": "language_display_name",'
  version = ('  "source":\n'
             '    {\n'
             '      "repository": "conformance-test",\n'
             '      "version": "trunk"\n'
             '    },')
  source =   '  "url": "No URL yet.",'
  end = '}'
  verify_head = '{\n  "Test scenario": "language_display_name",'

  return [descr] + [test_id] + [version] + [source] + insertJObj(tests_obj, 2) + [end], [verify_head] + insertJObj(verify_obj, 2) + [end]


def insertNumberFmtDescr(tests_obj, verify_obj):
  descr =   ('{\n'
             '  "description": "Number formatter test cases. The skeleton entry corresponds to\\n'
             '  the formating specification used by ICU while the option entries adhere to\\n'
             '  ECMA-402 syntax.",')
  test_id =  '  "Test scenario": "number_fmt",'
  version = ('  "source":\n'
             '    {\n'
             '      "repository": "icu",\n'
             '      "version": "trunk"\n'
             '    },')
  source =   '  "url": "https://raw.githubusercontent.com/unicode-org/icu/main/icu4c/source/test/testdata/numberpermutationtest.txt",'
  end = '}'
  verify_head = '{\n  "Test scenario": "number_fmt",'

  return [descr] + [test_id] + [version] + [source] + insertJObj(tests_obj, 2) + [end], [verify_head] + insertJObj(verify_obj, 2) + [end]


def processDcmlFmtTestDataObjects(rawtestdata):
  testdata_object_list, verify_object_list = generateDcmlFmtTestDataObjects(rawtestdata, 0)
  tests_object = generateTestsObject(testdata_object_list)
  verify_object = generateVerifyObject(verify_object_list)
  json_test, verify = insert_descr(tests_object, verify_object)

  return json_test, verify

def processNumberFmtTestData(rawnumfmttestdata, rawdcmlfmttestdata):
  num_testdata_object_list, num_verify_object_list, count = generateNumberFmtTestDataObjects(rawnumfmttestdata)
  dcml_testdata_object_list, dcml_verify_object_list = generateDcmlFmtTestDataObjects(rawdcmlfmttestdata, count)

  tests_object = generateTestsObject(num_testdata_object_list + dcml_testdata_object_list)
  verify_object = generateVerifyObject(num_verify_object_list + dcml_verify_object_list)
  json_test, verify = insertNumberFmtDescr(tests_object, verify_object)

  return json_test, verify


def processLangNameTestData(rawtestdata):
  testdata_object_list, verify_object_list = generateLanguageNameTestDataObjects(rawtestdata)
  tests_object = generateTestsObject(testdata_object_list)
  verify_object = generateVerifyObject(verify_object_list)
  json_test, verify = languageNameDescr(tests_object, verify_object)

  #for t in json_test:
  #  print(t)
  return json_test, verify


def main():
  print('Generating .json files for data driven testing')
  rawcolltestdata = readFile('CollationTest_SHIFTED_SHORT.txt')
  #rawtestdata = readFile('CollationTest_NON_IGNORABLE_SHORT.txt')
  json_test, json_verify = processTestData(rawcolltestdata)
  coll_test_file = open('coll_test_shift.json', 'w')
  for t in json_test:
    coll_test_file.write(t)
    coll_test_file.write('\n')
  coll_test_file.close()
  coll_verify_file = open('coll_verify_shift.json', 'w')
  for v in json_verify:
    coll_verify_file.write(v)
    coll_verify_file.write('\n')
  coll_verify_file.close()

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

  rawnumfmttestdata = readFile('numberpermutationtest.txt')
  num_fmt_test, num_fmt_verify = processNumberFmtTestData(rawnumfmttestdata, rawdcmlfmttestdata)
  num_fmt_test_file = open('num_fmt_test_file.json', 'w')
  for t in num_fmt_test:
    num_fmt_test_file.write(t)
    num_fmt_test_file.write('\n')
  num_fmt_test_file.close()
  num_fmt_verify_file = open('num_fmt_verify_file.json', 'w')
  for v in num_fmt_verify:
    num_fmt_verify_file.write(v)
    num_fmt_verify_file.write('\n')
  num_fmt_verify_file.close()

  rawlangnametestdata = readFile('languageNameTable.txt')
  lang_name_test, lang_name_verify = processLangNameTestData(rawlangnametestdata)
  lang_name_test_file = open('lang_name_test_file.json', 'w')
  for t in lang_name_test:
    lang_name_test_file.write(t)
    lang_name_test_file.write('\n')
  lang_name_test_file.close()
  lang_name_verify_file = open('lang_name_verify_file.json', 'w')
  for v in lang_name_verify:
    lang_name_verify_file.write(v)
    lang_name_verify_file.write('\n')
  lang_name_verify_file.close()
  print('================================================================================')


if __name__ == '__main__':
  main()
