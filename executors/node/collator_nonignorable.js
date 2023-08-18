// The Collator for nonignorable short tests.

// !!! TODO: Collation: determine the sensitivity that corresponds
// to the strength.
module.exports = {

  testCollationNonignorableShort: function(json) {

    // Global default locale
    let testLocale = '';
    let testCollOptions = {};

    // Set up collator object with optional locale and testOptions.
    let coll;
    try {
      if (testLocale) {
        coll = new Intl.Collator(testLocale, testCollOptions);
      } else {
        coll = new Intl.Collator(testCollOptions);
      }
      let d1 = json['string1'];
      let d2 = json['string2'];

      const compared = coll.compare(d1, d2);
      let result = compared<= 0 ? true : false;
      let resultString = result ? true : false;
      outputLine = {'label':json['label'],
                    "result": result
                   }

      if (result != true) {
        // Additional info for the comparison
        outputLine['compare'] = compared;
      }

    } catch (error) {
      outputLine =  {'label': json['label'],
                     'error_message': error.message,
                     'error': 'Collator compare failed'
                 };
    }
    return outputLine;
  }
};
