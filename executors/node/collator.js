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

    let compare_type = undefined;
    if ('compare_type' in json) {
      compare_type = json['compare_type'];
    }

    // Set up collator object with optional locale and testOptions.
    let coll;
    try {
      coll = new Intl.Collator(testLocale, testCollOptions);

      let d1 = json['s1'];
      let d2 = json['s2'];

      // Should we check with < or <=?
      const compared = coll.compare(d1, d2);

      let result = undefined;
      // Check for strict equality comparison
      if (compare_type && compare_type == '=' && compared == 0) {
        result = true;
      } else {
        result = (compared == 0);
      }

      outputLine = {'label':json['label'],
                   }
      if (result == true) {
        // Only output result field if result is true.
        outputLine['result'] = result;
        outputLine['compare_result'] = compared;
      } else {
        // Additional info for the comparison
        outputLine['compare'] = compared;
        if (rules) {
          outputLine['unsupported'] = 'Collator rules not available';
          outputLine['error_detail'] = 'Rules not supported';
          outputLine['error'] = 'rules';
        }
        else if (compare_type) {
          outputLine['unsupported'] = 'Compare type not supported';
          outputLine['error_detail'] = 'No comparison';
          outputLine['error'] = 'compare_type';
        }
      }

    } catch (error) {
      outputLine =  {
        'label': json['label'],
        'error_message': 'LABEL: ' + json['label'] + ' ' + error.message,
        'error': 'Collator compare failed'
      };
    }
    return outputLine;
  }
};
