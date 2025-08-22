// The Collator used for the actual testing.

import 'dart:convert';

import 'package:intl4x/collation.dart';
import 'package:intl4x/intl4x.dart';

String testCollation(String jsonEncoded) {
  final json = jsonDecode(jsonEncoded) as Map<String, dynamic>;
  // Global default locale
  final outputLine = <String, dynamic>{'label': json['label']};
  if (json.containsKey('rules')) {
    outputLine['error_type'] = 'unsupported';
    outputLine['unsupported'] = 'unsupported_options';
    outputLine['error_message'] = 'Rules are not supported';
    return jsonEncode(outputLine);
  }
  final localeString = json['locale'] as String? ?? 'en';
  if (localeString == 'root') {
    outputLine['error_type'] = 'unsupported';
    outputLine['unsupported'] = 'unsupported_options';
    outputLine['error_message'] = 'Locale `root` is unsupported';
    return jsonEncode(outputLine);
  }
  // Set up collator object with optional locale and testOptions.
  final s1 = json['s1'];
  final s2 = json['s2'];

  // Get options
  final ignorePunctuation = json['ignorePunctuation'] as bool? ?? false;
  final sensitivity = switch (json['strength']) {
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
  final compareType = json['compare_type'] as String?;

  if (s1 == null || s2 == null) {
    outputLine.addAll({
      'error': 'Collator failed to get s1 and s2',
      's1': s1,
      's2': s2,
    });
  } else {
    try {
      final coll = Intl(locale: Locale.parse(localeString));

      final collationOptions = CollationOptions(
        ignorePunctuation: ignorePunctuation,
        sensitivity: sensitivity,
        numeric: numeric,
        caseFirst: caseFirst,
      );

      final compared = coll.collation(collationOptions).compare(s1, s2);

      bool result;
      if (compareType == '=') {
        // Check for strict equality comparison
        result = compared == 0;
      } else if (compareType != null && compareType.startsWith('<')) {
        // Check results with different compare types
        result = compared < 0;
      } else {
        result = compared <= 0;
      }
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
