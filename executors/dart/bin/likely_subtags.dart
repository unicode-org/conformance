import 'dart:convert';

import 'package:intl4x/intl4x.dart';

String testLikelySubtags(String jsonEncoded) {
  final json = jsonDecode(jsonEncoded) as Map<String, dynamic>;

  final label = json['label'] as String?;
  final localeStr = json['locale'] as String;
  final testOption = json['option'] as String;
  final outputLine = <String, dynamic>{'label': label};

  try {
    final locale = Locale.parse(localeStr.replaceAll('_', '-'));
    String resultLocale;
    if (testOption == 'maximize') {
      resultLocale = locale.maximize().toLanguageTag();
    } else if (testOption == 'minimizeFavorScript' ||
        testOption == 'minimize') {
      resultLocale = locale.minimize().toLanguageTag();
    } else if (testOption == 'minimizeFavorRegion') {
      throw UnimplementedError();
    } else {
      throw ArgumentError('Unknown test option = $testOption');
    }
    outputLine['result'] = resultLocale;
  } catch (error) {
    outputLine.addAll({
      'error_message': error.toString(),
      'unsupported': 'unsupported subtags',
      'error_type': 'unsupported',
      'error': 'Failure in locale subtags.'
    });
  }
  return jsonEncode(outputLine);
}
