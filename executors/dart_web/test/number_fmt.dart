import 'dart:async';
import 'dart:convert';

import 'package:test/test.dart';

import '../bin/numberformat.dart';

void main() {
  testWithFormatting(
    'Check number format output',
    () {
      final inputLine = {
        'label': '2137',
        'locale': 'zh-TW',
        'skeleton': 'measure-unit/length-furlong unit-width-narrow .000',
        'input': '91827.3645',
        'options': {
          'style': 'unit',
          'unit': 'furlong',
          'unitDisplay': 'narrow',
          'currencyDisplay': 'narrowSymbol',
          'maximumFractionDigits': 3,
          'minimumFractionDigits': 3
        }
      };
      final outputLine = testDecimalFormat(jsonEncode(inputLine));
      print(outputLine);
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
