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
  Map<String, dynamic> outputLine;

  // Set up collator object with optional locale and testOptions.
  try {
    Intl coll;
    if (testLocale.isNotEmpty) {
      coll = Intl(locale: Locale.parse(testLocale));
    } else {
      coll = Intl();
    }

    var d1 = '';
    var d2 = '';
    try {
      d1 = json['s1'];
      d2 = json['s2'];
    } catch {
      outputLine = {
        'label': json['label'],
        'error_message': error.toString(),
        'error': 'Collator failed to get s1 and s2',
        's1': d1, 's2': d2
      };
      return jsonEncode(outputLine);
    }
    final collationOptions = CollationOptions(
      ignorePunctuation: bool.ltryParse(json['ignorePunctuation']) ?? false,
    );

    final compared = coll.collation(collationOptions).compare(d1, d2);
    final result = compared <= 0 ? true : false;
    outputLine = {'label': json['label'], "result": result};

    if (result != true) {
      // Additional info for the comparison
      outputLine['compare'] = compared;
    }
  } catch (error) {
    outputLine = {
      'label': json['label'],
      'error_message': error.toString(),
      'error': 'Collator compare failed',
      's1': d1, 's2': d2
    };
  }
  return jsonEncode(outputLine);
}
