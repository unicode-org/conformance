import 'dart:convert';

import 'package:intl4x/display_names.dart';
import 'package:intl4x/intl4x.dart';

String testLangNames(String jsonEncoded) {
  final json = jsonDecode(jsonEncoded) as Map<String, dynamic>;

  final outputLine = <String, dynamic>{};

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
        'error': 'locale_label: ' + error.toString(),
        'label': json['label'],
        'test_type': 'display_names',
        'error_type': 'unsupported',
        'error_detail': 'locale_label',
        'error_retry': false // Do not repeat
    });
    return jsonEncode(outputLine);
  }

  final languageLabel =
  (json['language_label'] as String).replaceAll('_', '-');

  try {
    final options = DisplayNamesOptions(
      languageDisplay: LanguageDisplay.standard,
    );
    final displayNames = Intl(locale: locale).displayNames(options);
    final resultLocale = displayNames.ofLanguage(Locale.parse(languageLabel));

    outputLine['label'] = json['label'];
    outputLine['result'] = resultLocale;
  } catch (error) {
    outputLine.addAll({
        //      'error': error.toString() + " language_label:" + languageLabel,
        'error': 'something went wrong: ' + error.toString(),
        'label': json['label'],
        'locale_label': locale.toLanguageTag(),
        'language_label': languageLabel,
        'test_type': 'display_names',
        'error_type': 'unsupported',
        'error_detail': languageLabel,
        'error_retry': false // Do not repeat
    });
  }
  return jsonEncode(outputLine);
}
