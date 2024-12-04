// The Collator used for the actual testing.

const debug = null;

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

    // Get other fields if provided
    let rules = undefined;
    if ('rules' in json) {
      rules = json['rules'];
    }

    let compare_type = undefined;
    if ('compare_type' in json) {
      compare_type = json['compare_type'].trim();
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

      let result = undefined;
      // Check for strict equality comparison
      if (compare_type) {
        compare_type = compare_type.replace('&lt;', '<');
        if (debug) {
          console.log('COMPARE_TYPE: |', compare_type, '| compared =', compared);
        }
        if (compare_type == '=' && compared == 0) {
          result = true;
        } else
        // Check results with different compare types
        if (compare_type[0] == '<' && compared < 0) {
          result = true;
        }
      } else {
        result = (compared <=  0);
      }

      outputLine = {'label':json['label'],
                   }
      outputLine['result'] = result;
      if (result == true) {
        outputLine['compare_result'] = compared;
      } else {
        // Additional info for the comparison
        outputLine['compare'] = compared;
        if (rules) {
          outputLine['unsupported'] = 'Collator rules not available';
          outputLine['error_detail'] = 'Rules not supported';
        }
        else if (compare_type) {
          outputLine['unsupported'] = 'Compare type ' + compare_type + ' not supported';
          // outputLine['options'] = testCollOptions;
          outputLine['error_detail'] = 'No comparison';
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
