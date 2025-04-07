// ignore_for_file: constant_identifier_names

import 'dart:convert';
import 'dart:io';

import 'package:dart_executor/collator.dart';
import 'package:dart_executor/lang_names.dart';
import 'package:dart_executor/numberformat.dart';
import 'package:dart_executor/version.dart' show intl4xVersion;

Map<String, List<String>> supportedTests = {
  'supported_tests': ['collation'],
};

enum TestTypes {
  collation,
  decimal_fmt,
  datetime_fmt,
  display_names,
  lang_names,
  number_fmt,
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

      final testType = TestTypes.values.firstWhere(
        (type) => type.name == decoded['test_type'],
      );
      final result = switch (testType) {
        TestTypes.collation => testCollation(line),
        TestTypes.decimal_fmt => testDecimalFormat(line),
        TestTypes.datetime_fmt => throw UnimplementedError(),
        TestTypes.display_names => throw UnimplementedError(),
        TestTypes.lang_names => testLangNames(line),
        TestTypes.number_fmt => testDecimalFormat(line),
      };

      final outputLine = {'label': decoded['label'], 'result': result};
      print(json.encode(outputLine));
    }
  }
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
