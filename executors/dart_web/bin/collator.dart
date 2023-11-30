// The Collator used for the actual testing.

// !!! TODO: Collation: determine the sensitivity that corresponds
// to the strength.
import 'dart:convert';

import 'package:intl4x/collation.dart';
import 'package:intl4x/intl4x.dart';

String testCollationShort(String jsonEncoded) {
  final json = jsonDecode(jsonEncoded)
      as Map<String, dynamic>; // For the moment, use strings for easier interop
  // Global default locale
  final testLocale = 'en';
  final Map<String, dynamic> outputLine = {'label': json['label']};

  // Set up collator object with optional locale and testOptions.
  final s1 = json['s1'];
  final s2 = json['s2'];
  final ignorePunctuation = bool.tryParse(json['ignorePunctuation'].toString());

  if (s1 == null || s2 == null) {
    outputLine.addAll({
      'error': 'Collator failed to get s1 and s2',
      's1': s1,
      's2': s2,
    });
  } else {
    try {
      Intl coll;
      if (testLocale.isNotEmpty) {
        coll = Intl(locale: Locale.parse(testLocale));
      } else {
        coll = Intl();
      }

      final collationOptions = CollationOptions(
        ignorePunctuation: ignorePunctuation ?? false,
      );

      final compared = coll.collation(collationOptions).compare(s1, s2);
      final result = compared <= 0;
      outputLine['result'] = result;

      if (result != true) {
        // Additional info for the comparison
        outputLine['compare'] = compared;
      }
    } catch (error) {
      outputLine.addAll({
        'error_message': error.toString(),
        'error': 'Collator compare failed',
        's1': s1,
        's2': s2,
      });
    }
  }
  return jsonEncode(outputLine);
}
