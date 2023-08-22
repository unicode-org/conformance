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
    var d1 = json['s1'];
    var d2 = json['s2'];

    var should_ignore_punctuation = false;
    try {
      // Check the setting of this options
      var ignorePunc = json['ignorePunctuation'];
      should_ignore_punctuation = ignorePunc;
    } catch (error) {
      continue;
    }
      
    var collationOptions = CollationOptions(ignorePunctuation: should_ignore_punctuation);

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
      'error': 'Collator compare failed',
      's1': d1, 's2': d2
    };
  }
  return jsonEncode(outputLine);
}
