import 'dart:convert';

import 'package:intl4x/display_names.dart';

String testLangNames(String jsonEncoded) {
  final json = jsonDecode(jsonEncoded) as Map<String, dynamic>;

  final outputLine = <String, dynamic>{'label': json['label']};

  final Locale locale;
  try {
    if (json['locale_label'] != null) {
      final localeJson = json['locale_label'] as String;
      locale = Locale.parse(localeJson);
    } else {
      locale = Locale.parse('en');
    }
  } catch (error) {
    outputLine.addAll({
      'error_detail': 'locale_label: $error',
      'error_type': 'unsupported',
      'error_retry': false, // Do not repeat
    });
    return jsonEncode(outputLine);
  }

  final languageLabel = json['language_label'] as String;
  if (languageLabel.contains('u-kr')) {
    outputLine.addAll({
      'unsupported': 'u-kr extension not supported',
      'error_retry': false, // Do not repeat
    });
    return jsonEncode(outputLine);
  }
  final languageDisplay = LanguageDisplay.values.firstWhere(
    (element) => element.name == json['languageDisplay'],
  );

  Locale languageLabelLocale;
  try {
    languageLabelLocale = Locale.parse(languageLabel);
  } catch (error) {
    // Something was not supported in this locale identifier
    outputLine.addAll({
      'error_type': 'unsupported',
      'error_detail': error.toString(),
      'error_retry': false, // Do not repeat
    });
    return jsonEncode(outputLine);
  }

  try {
    final displayNames = DisplayNames(
      locale: locale,
      languageDisplay: languageDisplay,
    );
    final resultLangName = displayNames.ofLocale(languageLabelLocale);

    outputLine['result'] = resultLangName;
  } catch (error) {
    outputLine.addAll({
      'error_detail': error.toString(),
      'actual_options': {
        'languageDisplay': LanguageDisplay.standard.toString(),
        'locale': locale.toString(),
      },
      'error_retry': false, // Do not repeat
    });
  }
  return jsonEncode(outputLine);
}
