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
      let result = compared<= 0 ? true : false;
      let result_bool = true;
      if (compared > 0) {
        result_bool = false;
      }
      outputLine = {'label':json['label'],
                   }
      if (result == true) {
        // Only output result field if result is true.
        outputLine['result'] = result_bool;
        outputLine['compare_result'] = compared;
      } else {
        // Additional info for the comparison
        outputLine['compare'] = compared;
        if (rules) {
          outputLine['unsupported'] = 'Collator rules not available';
          outputLine['error_detail'] = 'No rules';
          outputLine['error'] = 'rules';
        }
        else {
          outputLine['actual_options'] = JSON.stringify(coll.resolvedOptions());  //.toString();
          outputLine['compare_result'] = compared;
          outputLine['result'] = result_bool;
        }
      }

    } catch (error) {
      const error_message = error.message;

      if (testLocale == "root" || error_message == "Incorrect locale information provided")  {
        outputLine =  {'label': json['label'],
                       'unsupported': 'root locale',
                       'error_detail': error_message + ': ' + testLocale,
                       'error': 'Unsupported locale'
                      };
      } else {
        outputLine =  {'label': json['label'],
                       'error_message': error_message,
                       'error_detail': testLocale,
                       'error': 'Something wrong'
                      };
      }
    }
    return outputLine;
  }
};
