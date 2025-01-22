// ignore_for_file: constant_identifier_names

import 'dart:convert';
import 'dart:io';
import 'package:intl4x/collation.dart';
import 'package:intl4x/intl4x.dart';

import 'version.dart';

Map<String, List<String>> supportedTests = {
  'supported_tests': [
    'collation',
  ],
};

enum TestTypes {
  collation,
  decimal_fmt,
  datetime_fmt,
  display_names,
  lang_names,
  number_fmt;
}

void main() {
  while (true) {
    final line = stdin.readLineSync();
    if (line == null) {
      exit(0);
    }
    if (line == '#EXIT') {
      exit(0);
    } else if (line == '#VERSION') {
      printVersion();
    } else if (line == '#TESTS') {
      print(json.encode(supportedTests));
    } else {
      Map<String, dynamic> decoded;
      try {
        decoded = json.decode(line);
      } catch (e) {
        throw 'ERRORSTART $line ERROREND';
      }

      final testType = TestTypes.values
          .firstWhere((type) => type.name == decoded['test_type']);
      Object result;
      switch (testType) {
        case TestTypes.collation:
          result = testCollator(decoded);
          break;
        case TestTypes.decimal_fmt:
        // TODO: Handle this case.
        case TestTypes.datetime_fmt:
        // TODO: Handle this case.
        case TestTypes.display_names:
        // TODO: Handle this case.
        case TestTypes.lang_names:
        // TODO: Handle this case.
        case TestTypes.number_fmt:
        // TODO: Handle this case.
        default:
          throw UnsupportedError('');
      }

      final outputLine = {'label': decoded['label'], 'result': result};
      print(json.encode(outputLine));
    }
  }
}

bool testCollator(Map<String, dynamic> decoded) {
  final ignorePunctuation = decoded['ignorePunctuation'] as bool?;
  final options =
      CollationOptions(ignorePunctuation: ignorePunctuation ?? false);

  final collation = Intl(locale: Locale(language: 'en')).collation(options);
  final compared = collation.compare(decoded['s1'], decoded['s2']);
  return compared <= 0;
}

void printVersion() {
  final version = Platform.version;
  final dartVersion = version.substring(0, version.indexOf(' '));
  final versionInfo = {
    'platform': 'Dart Native',
    'icuVersion': 73, //TODO: get from ICU4X somehow
    'platformVersion': dartVersion,
    'intlVersion': intl4xVersion,
  };
  print(json.encode(versionInfo));
}
