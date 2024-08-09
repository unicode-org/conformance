// ignore_for_file: constant_identifier_names

import 'dart:convert';
import 'dart:io';

import 'package:intl4x/collation.dart';
import 'package:intl4x/intl4x.dart';

import 'lang_names.dart';
import 'numberformat.dart';
import 'version.dart';

Map<String, List<String>> supportedTests = {
  'supported_tests': [
    'coll_shift_short',
  ],
};

enum TestTypes {
  collation_short,
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

      final testTypeStr = decoded['test_type'];
      final testType =
          TestTypes.values.firstWhere((type) => type.name == testTypeStr);
      final result = switch (testType) {
        TestTypes.collation_short => collation(decoded),
        TestTypes.decimal_fmt ||
        TestTypes.number_fmt =>
          testDecimalFormat(line),
        TestTypes.lang_names => testLangNames(line),
        TestTypes.datetime_fmt => throw UnimplementedError(),
        TestTypes.display_names => throw UnimplementedError(),
      };

      final outputLine = {'label': decoded['label'], 'result': result};
      print(json.encode(outputLine));
    }
  }
}

bool collation(Map<String, dynamic> decoded) {
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
