import 'dart:async';
import 'dart:convert';

import 'package:dart_web/collator.dart';
import 'package:dart_web/lang_names.dart';
import 'package:dart_web/numberformat.dart';
import 'package:meta/meta.dart';
import 'package:test/test.dart';

/// Run using `dart --enable-experiment=native-assets test -p chrome` for dart_web
/// and `dart --enable-experiment=native-assets test` for dart_native

void main() {
  testWithFormatting(
    'Check number format output',
    () {
      final inputLine = {
        'label': '4195',
        'locale': 'es-MX',
        'skeleton': 'unit-width-narrow .000 latin',
        'input': '91827.3645',
        'options': {
          'unitDisplay': 'narrow',
          'currencyDisplay': 'narrowSymbol',
          'minimumFractionDigits': 2,
          'maximumFractionDigits': 3,
          'numberingSystem': 'latn'
        }
      };
      final outputLine = testDecimalFormat(jsonEncode(inputLine));
      final decoded = jsonDecode(outputLine) as Map<String, dynamic>;
      expect(decoded['result'], '91,827.365');
    },
  );

  testWithFormatting(
    'Check collation output',
    () {
      final inputLine = {
        'label': '0001443',
        's1': '\t!',
        's2': '\t?',
        'line': 11,
        'source_file': 'CollationTest_SHIFTED_SHORT.txt',
        'ignorePunctuation': true,
        'hexhash': '902804509fbe1fafcb7c9de66b632474ebde8490'
      };
      final outputLine = testCollation(jsonEncode(inputLine));
      final decoded = jsonDecode(outputLine) as Map<String, dynamic>;
      expect(decoded['result'], true);
    },
  );

  testWithFormatting(
    'Check langnames output',
    () {
      final inputLine = {
        'label': '0001',
        'language_label': 'es',
        'locale_label': 'en',
        'languageDisplay': 'standard',
        'hexhash': 'd7f75c25feb271aac415acd19f0fe3954551ce0c'
      };
      final outputLine = testLangNames(jsonEncode(inputLine));
      final decoded = jsonDecode(outputLine) as Map<String, dynamic>;
      expect(decoded['result'], 'Spanish');
    },
  );
}

@isTest
void testWithFormatting<T>(
  dynamic description,
  T Function() body, {
  String? testOn,
  Timeout? timeout,
  dynamic skip,
  dynamic tags,
  Map<String, dynamic>? onPlatform,
  int? retry,
}) {
  test(
    description,
    () => runZoned(body, zoneValues: {#test.allowFormatting: true}),
    testOn: testOn,
    timeout: timeout,
    skip: skip,
    tags: tags,
    onPlatform: onPlatform,
    retry: retry,
  );
}
