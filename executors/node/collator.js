// The Collator used for the actual testing.

module.exports = {

  testCollationShort: function(json) {
    // Global default locale

    let outputLine = {'label':json['label']};

    // Locale if provided in the test data.
    let testLocale = undefined;
    testLocale = json['locale'];

    if (testLocale == 'root') {
      outputLine =  {'label': json['label'],
                     'error_message': "root locale",
                     'unsupported': 'root locale',
                     'error_detail': testLocale,
                     'error': 'Unsupported locale'
                    };
      return outputLine;
    }

    // Check if this locale is actually supported
    try {
      const supported_locales =
            Intl.Collator.supportedLocalesOf([testLocale], {localeMatcher: "best fit"});

      if (supported_locales.length == 1 && supported_locales[0] != testLocale) {
        testLocale = supported_locales[0];
        outputLine['substituted_locale'] = testLocale;;
      }
      else if (supported_locales.length <= 0 ||
               !supported_locales.includes(testLocale)) {
        // Report as unsupported
        outputLine['error_message'] = "unsupported locale";
        outputLine['unsupported'] = testLocale;
        outputLine['error_detail'] = supported_locales;
        outputLine['error'] = "unsupported locale";
        return outputLine;
      }
    } catch (error) {
      console.log("ERROR @ 44 ", error.name, " ", error.message);
      console.log(" testLocale = ", testLocale);
      outputLine['unsupported'] = "supportedLocalsOf";
      outputLine['error_message'] = error.message;
      outputLine['error_detail'] = testLocale;
      outputLine['error'] = error.name;
      return outputLine;
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
        testCollOptions['sensitivity'] = 'variant';
      }
    }

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
        outputLine['actual_options'] = {
          'compared_result': compared,
          's1': d1,
          's2': d2,
          'options': JSON.stringify(coll.resolvedOptions())
        };
        outputLine['compare_result'] = compared;
        outputLine['result'] = result;
      }

    } catch (error) {
      const error_message = error.message;
      console.log('ERROR @ 135: ', error);
      if (error_message == "Incorrect locale information provided")  {
        outputLine =  {'label': json['label'],
                       'error_message': error.message,
                       'unsupported': 'UNSUPPORTED',
                       'error_detail': error_message + ': ' + testLocale,
                       'actual_options': JSON.stringify(coll.resolvedOptions()),
                      };
      } else {
        console.log("ERROR @ 144 ", error.name, " ", error.message);
        // Another kind of error.
        outputLine =  {'label': json['label'],
                       'error_message': error.message,
                       'error_detail': testLocale,
                       'error': error.name,
                       'actual_options': JSON.stringify(coll.resolvedOptions()),
                      };
      }
    }
    return outputLine;
  }
};
