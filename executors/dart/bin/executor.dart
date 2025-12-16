// ignore_for_file: constant_identifier_names

import 'dart:convert';
import 'dart:io';

import 'package:collection/collection.dart';
import 'package:dart_executor/collator.dart';
import 'package:dart_executor/datetime_format.dart';
import 'package:dart_executor/lang_names.dart';
import 'package:dart_executor/list_format.dart';
import 'package:dart_executor/numberformat.dart';
import 'package:dart_executor/plural_rules.dart';
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
  likely_subtags,
  list_fmt,
  plural_rules,
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
      try {
        final testType = TestTypes.values.firstWhereOrNull(
          (type) => type.name == decoded['test_type'],
        );
        final outputLine = switch (testType) {
          TestTypes.collation => testCollation(line),
          TestTypes.decimal_fmt => testDecimalFormatWrapped(line),
          TestTypes.number_fmt => testDecimalFormatWrapped(line),
          TestTypes.datetime_fmt => testDateTimeFmt(line),
          TestTypes.display_names => throw UnimplementedError(
            'display_names is not supported yet',
          ),
          TestTypes.lang_names => testLangNames(line),
          // TestTypes.likely_subtags => testLikelySubtags(line),
          TestTypes.likely_subtags => throw UnimplementedError(
            'likely_subtags is not supported yet, as the Locale object is not yet migrated to ICU4X',
          ),
          TestTypes.list_fmt => testListFmt(line),
          TestTypes.plural_rules => testPluralRules(line),
          null => throw ArgumentError.value(
            decoded['test_type'],
            'Unknown test type',
          ),
        };
        print(outputLine);
      } catch (e, s) {
        throw ArgumentError('Error while executing on $line. Error was:\n $e \n $s');
      }
    }
  }
}

void printVersion() {
  final version = Platform.version;
  final dartVersion = version.substring(0, version.indexOf(' '));
  final versionInfo = {
    'platform': 'Dart Native',
    'icuVersion': '77', //TODO: get from ICU4X somehow
    'platformVersion': dartVersion,
    'intlVersion': intl4xVersion,
  };
  print(json.encode(versionInfo));
}
