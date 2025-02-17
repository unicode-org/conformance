import 'dart:async';
import 'dart:convert';

import 'package:test/test.dart';

import '../bin/numberformat.dart';

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
          'maximumFractionDigits': 3,
          'minimumFractionDigits': 3,
          'numberingSystem': 'latn'
        }
      };
      final outputLine = testDecimalFormat(jsonEncode(inputLine));
      final decoded = jsonDecode(outputLine) as Map<String, dynamic>;
      expect(decoded['result'], '91,827.364');
    },
    testOn: 'browser',
  );
}

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
