// The Collator used for the actual testing.

// Collation: determine the sensitivity that corresponds to the strength.
module.exports = {

  testCollationShort: function(json) {
    // Global default locale

    // Locale if provided in the test data.
    let testLocale = undefined;
    if ('locale' in json) {
      testLocale = json['locale'];
    }
    let testCollOptions = {};
    if ('ignorePunctuation' in json) {
      testCollOptions = {
        ignorePunctuation:json['ignorePunctuation']}
    }

    // Get other fields if provided
    let rules = undefined;
    if ('rules' in json) {
      rules = json['rules'];
    }

    // Set up collator object with optional locale and testOptions.
    let coll;
    try {
      coll = new Intl.Collator(testLocale, testCollOptions);

      let d1 = json['s1'];
      let d2 = json['s2'];

      // Should we check with < or <=?
      const compared = coll.compare(d1, d2);
      let result = compared<= 0 ? true : false;
      let result_bool = true;
      if (compared > 0) {
        result_bool = false;
      }
      outputLine = {'label':json['label'],
                    'result': result_bool,
                    'compare_result': compared,
                   }

      if (result != true) {
        // Additional info for the comparison
        outputLine['compare'] = compared;
      }

    } catch (error) {
      outputLine =  {'label': json['label'],
                     'error_message': 'LABEL: ' + json['label'] + ' ' + error.message,
                     'error': 'Collator compare failed'
                 };
    }
    return outputLine;
  }
};
