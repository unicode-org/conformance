import 'dart:convert';

import 'package:collection/collection.dart';
import 'package:intl4x/intl4x.dart';
import 'package:intl4x/plural_rules.dart';

/// Tests Intl Locale for plural rules.
///
/// This function translates the logic from the given JavaScript code,
/// using the `intl4x` package for `Intl.PluralRules` functionality.
String testPluralRules(String jsonEncoded) {
  final json = jsonDecode(jsonEncoded) as Map<String, dynamic>;

  final label = json['label'];
  final returnJson = {'label': label};

  var localeString = (json['locale'] as String).replaceAll('_', '-');
  if (localeString == 'root') {
    returnJson['warning'] = 'locale <root> replaced with <und>';
    localeString = 'und';
  }

  // Locale parsing
  final Locale locale;
  try {
    locale = Locale.parse(localeString);
  } catch (e) {
    returnJson.addAll({
      'error': 'unsupported',
      'unsupported': 'invalid_locale_format',
      'error_detail': {'locale': localeString, 'message': e.toString()},
    });
    return jsonEncode(returnJson);
  }

  num? sample;
  if (json['sample'] != null) {
    final rawSample = json['sample'] as String;
    if (rawSample.contains('c')) {
      return jsonEncode({
        'label': label,
        'error': 'unsupported',
        'unsupported': 'unsupported compact number',
        'error_detail': {'unsupported sample': json['sample']},
      });
    }
    if (rawSample.contains('.')) {
      sample = double.tryParse(rawSample);
    } else {
      sample = int.tryParse(rawSample);
    }

    if (sample == null) {
      returnJson['error'] = 'Invalid sample format';
      return jsonEncode(returnJson);
    }
  } else {
    returnJson['error'] = 'Incomplete test: no sample included';
    return jsonEncode(returnJson);
  }

  // PluralRulesOptions setup
  var testOptions = PluralRulesOptions();
  final typeString = json['type'] as String?;
  if (typeString != null) {
    final pluralType = Type.values.firstWhereOrNull(
      (type) => typeString == type.name,
    );
    if (pluralType != null) {
      testOptions = testOptions.copyWith(type: pluralType);
    } else {
      returnJson.addAll({
        'error': 'unsupported',
        'unsupported': 'unsupported_plural_type',
        'error_detail': {'type': typeString},
      });
      return jsonEncode(returnJson);
    }
  }

  final intl = Intl(locale: locale);
  final pluralRules = intl.plural(testOptions);

  try {
    final result = pluralRules.select(sample);
    returnJson['result'] = result.name;
  } catch (error) {
    returnJson['error'] = 'PLURAL RULES UNKNOWN ERROR: ${error.toString()}';
  }
  return jsonEncode(returnJson);
}
