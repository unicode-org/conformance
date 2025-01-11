// The Collator used for the actual testing.

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
      testCollOptions['ignorePunctuation'] = json['ignorePunctuation'];
    }

    if ('numeric' in json) {
      testCollOptions['numeric'] = true;
    }
    if ('caseFirst' in json) {
      testCollOptions['caseFirst'] = json['case_first'];
    }
    const strength = json['strength'];
    if (strength) {
      if (strength == 'primary') {
        testCollOptions['sensitivity'] = 'base';
      } else
      if (strength == 'secondary') {
        testCollOptions['sensitivity'] = 'accent';
      } else
      if (strength == 'tertiary') {
        testCollOptions['sensitivity'] = 'case';
      }
    }

    let outputLine = {'label':json['label']};
    // Get other fields if provided
    let rules = undefined;
    if ('rules' in json) {
      rules = json['rules'];
      outputLine['unsupported'] = 'Collator rules not available';
      outputLine['error_detail'] = 'Rules not supported';
      return outputLine;
    }

    let compare_type;
    if ('compare_type' in json) {
      compare_type = json['compare_type'].trim();
      compare_type = compare_type.replace('&lt;', '<');
    }

    let reoder;
    if ('reorder' in json) {
      reorder = json['reorder'];
    }

    // Set up collator object with optional locale and testOptions.
    let coll;
    try {
      coll = new Intl.Collator(testLocale, testCollOptions);

      let d1 = json['s1'];
      let d2 = json['s2'];

      // Should we check with < or <=?
      const compared = coll.compare(d1, d2);

      let result = false;
      // Check for strict equality comparison
      if (compare_type) {
        if (compare_type == '=' && compared == 0) {
          result = true;
        } else
        // Check results with different compare types
        if (compare_type[0] == '<' && compared < 0) {
          result = true;
        }
      } else {
        // Default comparison method.
        result = (compared <=  0);
      }

      outputLine['result'] = result;
      if (result == true) {
        outputLine['compare_result'] = compared;
      } else {
        // Additional info for the comparison
        outputLine['actual_options'] = JSON.stringify(coll.resolvedOptions());
        outputLine['compare_result'] = compared;
        outputLine['result'] = result;
      }

    } catch (error) {
      const error_message = error.message;
      if (testLocale == "root" ||
          error_message == "Incorrect locale information provided")  {
        outputLine =  {'label': json['label'],
                       'error_message': error.message,
                       'unsupported': 'root locale',
                       'error_detail': error_message + ': ' + testLocale,
                       'error': 'Unsupported locale'
                      };
      } else {
        // Another kind of error.
        outputLine =  {'label': json['label'],
                       'error_message': error.message,
                       'error_detail': testLocale,
                       'error': error.name
                      };
      }
    }
    return outputLine;
  }
};
