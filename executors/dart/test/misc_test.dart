import 'dart:async';
import 'dart:convert';

import 'package:dart_executor/collator.dart';
import 'package:dart_executor/datetime_format.dart';
import 'package:dart_executor/lang_names.dart';
import 'package:dart_executor/numberformat.dart';
import 'package:intl4x/datetime_format.dart';
import 'package:meta/meta.dart';
import 'package:test/test.dart';

/// Run using `dart --enable-experiment=native-assets,record-use test -p chrome` for dart_web
/// and `dart --enable-experiment=native-assets,record-use test` for dart_native

void main() {
  testWithFormatting('Check number format output', () {
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
        'numberingSystem': 'latn',
      },
    };
    final outputLine = testDecimalFormatWrapped(jsonEncode(inputLine));
    final decoded = jsonDecode(outputLine) as Map<String, dynamic>;
    expect(decoded['result'], '91,827.365');
  });

  testWithFormatting('Check collation output', () {
    final inputLine = {
      'label': '0001443',
      's1': '\t!',
      's2': '\t?',
      'line': 11,
      'source_file': 'CollationTest_SHIFTED_SHORT.txt',
      'ignorePunctuation': true,
      'hexhash': '902804509fbe1fafcb7c9de66b632474ebde8490',
    };
    final outputLine = testCollation(jsonEncode(inputLine));
    final decoded = jsonDecode(outputLine) as Map<String, dynamic>;
    expect(decoded['result'], true);
  });

  testWithFormatting('Check langnames output', () {
    final inputLine = {
      'label': '0001',
      'language_label': 'es',
      'locale_label': 'en',
      'languageDisplay': 'standard',
      'hexhash': 'd7f75c25feb271aac415acd19f0fe3954551ce0c',
    };
    final outputLine = testLangNames(jsonEncode(inputLine));
    final decoded = jsonDecode(outputLine) as Map<String, dynamic>;
    expect(decoded['result'], 'Spanish');
  });

  testWithFormatting('decimal format compact', () {
    final input = {
      'label': '0730',
      'locale': 'es-MX',
      'skeleton': 'compact-short unit-width-narrow @@',
      'input': '91827.3645',
      'options': {
        'notation': 'compact',
        'compactDisplay': 'short',
        'unitDisplay': 'narrow',
        'currencyDisplay': 'narrowSymbol',
        'maximumSignificantDigits': 2,
        'minimumSignificantDigits': 2,
      },
      'hexhash': '95514d4fd3ab3f2a24c86bb0e0f21c8f7ec57142',
    };
    final outputLine = testDecimalFormatWrapped(jsonEncode(input));
    final output = jsonDecode(outputLine) as Map<String, dynamic>;
    expect(output['result'], '92 k');
  }, skip: 'Failing for now');

  testWithFormatting('datetime format short', () {
    final input = {
      'label': '048',
      'locale': 'en',
      'input_string': '2000-01-01T00:00:00Z',
      'options': {
        'timeZone': 'Etc/GMT',
        'calendar': 'gregory',
        'zoneStyle': 'location',
        'skeleton': 'MdjmsVVVV',
        'semanticSkeleton': 'MDTZ',
        'semanticSkeletonLength': 'short',
      },
      'tz_offset_secs': 0,
      'original_input': '2000-01-01T00:00Z[Etc/GMT]',
      'hexhash': '3b045161836e839e3d19eefc37c1d6923ba63615',
    };
    final outputLine = testDateTimeFmt(jsonEncode(input));
    final output = jsonDecode(outputLine) as Map<String, dynamic>;
    print(
      DateTimeFormat.yearMonthDayTime(
        locale: Locale.parse(input['locale'] as String),
      ).format(DateTime.parse(input['input_string'] as String)),
    );
    expect(output['result'], '1/1, 12:00:00 AM GMT');
  }, skip: 'Failing for now');
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
