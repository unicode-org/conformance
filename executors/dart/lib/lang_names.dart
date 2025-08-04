import 'dart:convert';

import 'package:intl4x/display_names.dart';
import 'package:intl4x/intl4x.dart';

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

  final options = DisplayNamesOptions(
    languageDisplay: LanguageDisplay.standard,
  );
  try {
    final displayNames = Intl(locale: locale).displayNames(options);
    final resultLangName = displayNames.ofLanguage(languageLabelLocale);

    outputLine['result'] = resultLangName;
  } catch (error) {
    outputLine.addAll({
      'error_type': 'unsupported',
      'error_detail': error.toString(),
      'actual_options': options.toJson(),
      'error_retry': false, // Do not repeat
    });
  }
  return jsonEncode(outputLine);
}

extension on DisplayNamesOptions {
  Map<String, String> toJson() => {
    'style': style.name,
    'languageDisplay': languageDisplay.name,
    'fallback': fallback.name,
  };
}
