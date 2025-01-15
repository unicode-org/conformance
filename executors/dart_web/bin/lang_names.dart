import 'dart:convert';

import 'package:intl4x/display_names.dart';
import 'package:intl4x/intl4x.dart';

String testLangNames(String jsonEncoded) {
  final json = jsonDecode(jsonEncoded) as Map<String, dynamic>;

  final outputLine = <String, dynamic>{};
  outputLine.addAll(
    'label': json['label']
  );

  final Locale locale;
  try {
    if (json['locale_label'] != null) {
      // Fix to use dash, not underscore.
      final localeJson = json['locale_label'] as String;
      locale = Locale.parse(localeJson.replaceAll('_', '-'));
    } else {
      locale = Locale(language: 'en');
    }
  } catch(error) {
    outputLine.addAll({
        'error_detail': 'locale_label: $error',
        'error_type': 'unsupported',
        'error_retry': false // Do not repeat
    });
    return jsonEncode(outputLine);
  }

  final languageLabel =
  (json['language_label'] as String).replaceAll('_', '-');
  try {
    final languageLabelLocale = Locale.parse(languageLabel);
  } catch (error) {
    // Something was not supported in this locale identifier
    outputLine.addAll({
        'error_type': 'unsupported',
        'error_detail': error.toString(),
        'error_retry': false // Do not repeat
    });
    return jsonEncode(outputLine);
  }

  try {
    final options = DisplayNamesOptions(
      languageDisplay: LanguageDisplay.standard,
    );
    final displayNames = Intl(locale: locale).displayNames(options);
    final resultLangName = displayNames.ofLanguage(Locale.parse(languageLabel));

    outputLine['result'] = resultLangName;
  } catch (error) {
    outputLine.addAll({
        'error_type': 'unsupported',
        'error_detail': error_toString(),
        'actual_options': options,
        'error_retry': false // Do not repeat
    });
  }
  return jsonEncode(outputLine);
}
