// The Collator used for the actual testing.

import 'dart:convert';

import 'package:intl4x/collation.dart';
import 'package:intl4x/intl4x.dart';

String testCollation(String jsonEncoded) {
  final json =
      jsonDecode(jsonEncoded)
          as Map<
            String,
            dynamic
          >; // For the moment, use strings for easier interop
  // Global default locale
  final testLocale = json['locale'] as String? ?? 'en';
  final Map<String, dynamic> outputLine = {'label': json['label']};

  // Set up collator object with optional locale and testOptions.
  final s1 = json['s1'];
  final s2 = json['s2'];

  // Get options
  final ignorePunctuation = json['ignorePunctuation'] as bool? ?? false;
  final Sensitivity? sensitivity = switch (json['strength']) {
    'primary' => Sensitivity.base,
    'secondary' => Sensitivity.accent,
    'tertiary' => Sensitivity.caseSensitivity,
    null => null,
    String() => null,
    Object() => throw UnimplementedError('strength must be of type String?'),
  };
  final numeric = json.containsKey('numeric');
  final caseFirst =
      CaseFirst.values
          .where((value) => value.jsName == json['case_first'])
          .firstOrNull ??
      CaseFirst.localeDependent;

  if (s1 == null || s2 == null) {
    outputLine.addAll({
      'error': 'Collator failed to get s1 and s2',
      's1': s1,
      's2': s2,
    });
  } else {
    try {
      final coll = Intl(locale: Locale.parse(testLocale));

      final collationOptions = CollationOptions(
        ignorePunctuation: ignorePunctuation,
        sensitivity: sensitivity,
        numeric: numeric,
        caseFirst: caseFirst,
      );

      final compared = coll.collation(collationOptions).compare(s1, s2);
      final result = compared <= 0;
      outputLine['result'] = result;

      if (result != true) {
        // Additional info for the comparison
        outputLine['compare'] = compared;
      }
    } catch (error, s) {
      outputLine.addAll({
        'error_message': error.toString(),
        'stack': s.toString(),
        'error': 'Collator compare failed',
        's1': s1,
        's2': s2,
      });
    }
  }
  return jsonEncode(outputLine);
}
