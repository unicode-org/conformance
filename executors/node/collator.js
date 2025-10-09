// The Collator used for the actual testing.

module.exports = {

  testCollationShort: function(json) {
    // Global default locale

    let outputLine = {'label':json['label']};

    // Locale if provided in the test data.
    let test_locale = 'en';  // default
    if ('locale' in json) {
      test_locale = json['locale'];
    }

    if (test_locale == 'root') {
      outputLine =  {'label': json['label'],
                     'error_message': "root locale",
                     'unsupported': 'root locale',
                     'error_detail': test_locale,
                     'error': 'Unsupported locale'
                    };
      return outputLine;
    }

    // Check if this locale is actually supported
    try {
      const supported_locales =
            Intl.Collator.supportedLocalesOf([test_locale], {localeMatcher: "best fit"});

      if (supported_locales.length == 1 && supported_locales[0] != test_locale) {
        test_locale = supported_locales[0];
        outputLine['substituted_locale'] = test_locale;;
      }
      else if (supported_locales.length <= 0 ||
               !supported_locales.includes(test_locale)) {
        // Report as unsupported
        outputLine['error_message'] = "unsupported locale";
        outputLine['unsupported'] = test_locale;
        outputLine['error_detail'] = supported_locales;
        outputLine['error'] = "unsupported locale";
        return outputLine;
      }
    } catch (error) {
      outputLine['unsupported'] = "supportedLocalsOf";
      outputLine['error_message'] = error.message;
      outputLine['error_detail'] = test_locale;
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

    // Locale special cases
    if (test_locale.search('co-search') >= 0) {
      testCollOptions['usage'] = 'search';
    }

    if (test_locale.search('-kr-') >= 0) {
      // Unsupport if not already replaced by a substitued locale.
      outputLine =  {'label': json['label'],
                     'error_message': "unsupported locale extension",
                     'unsupported': '-kr-',
                     'error_detail': test_locale,
                     'error': 'Unsupported locale extension'
                    };
      return outputLine;
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

  let reorder;
  if ('reorder' in json) {
    reorder = json['reorder'];
  }

  // Set up collator object with optional locale and testOptions.
  let coll;
  try {
    coll = new Intl.Collator(test_locale, testCollOptions);

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
    if (error_message == "Incorrect locale information provided")  {
      outputLine =  {'label': json['label'],
                     'error_message': error.message,
                     'unsupported': 'UNSUPPORTED',
                     'error_detail': error_message + ': ' + test_locale,
                     'actual_options': JSON.stringify(coll.resolvedOptions()),
                    };
    } else {
      // Another kind of error.
      outputLine =  {'label': json['label'],
                     'error_message': error.message,
                     'error_detail': test_locale,
                     'error': error.name,
                     'actual_options': JSON.stringify(coll.resolvedOptions()),
                    };
    }
  }
  return outputLine;
}
};
