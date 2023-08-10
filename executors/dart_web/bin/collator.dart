// The Collator used for the actual testing.

// !!! TODO: Collation: determine the sensitivity that corresponds
// to the strength.
import 'dart:convert';

import 'package:intl4x/collation.dart';
import 'package:intl4x/intl4x.dart';

String testCollationShort(String jsonEncoded) {
  var json =
      jsonDecode(jsonEncoded); // For the moment, use strings for easier interop
  // Global default locale
  var testLocale = 'en';
  Map<String, dynamic> outputLine;

  // Set up collator object with optional locale and testOptions.
  try {
    Intl coll;
    if (testLocale.isNotEmpty) {
      coll = Intl(locale: Locale.parse(testLocale));
    } else {
      coll = Intl();
    }
    var d1 = json['string1'];
    var d2 = json['string2'];

    var collationOptions = CollationOptions(ignorePunctuation: true);
    var compared = coll.collation(collationOptions).compare(d1, d2);
    var result = compared <= 0 ? true : false;
    outputLine = {'label': json['label'], "result": result};

    if (result != true) {
      // Additional info for the comparison
      outputLine['compare'] = compared;
    }
  } catch (error) {
    outputLine = {
      'label': json['label'],
      'error_message': error.toString(),
      'error': 'Collator compare failed'
    };
  }
  return jsonEncode(outputLine);
}
