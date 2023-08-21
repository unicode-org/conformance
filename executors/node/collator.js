// The Collator used for the actual testing.

// !!! TODO: Collation: determine the sensitivity that corresponds
// to the strength.
module.exports = {

  testCollationShort: function(json, shifted) {

    // Global default locale
    let testLocale = undefined;
    // TODO: set locale if provided in the test data.

    let testCollOptions = {};
    if (shifted) {
       testCollOptions = {ignorePunctuation:true};
    }

    // Set up collator object with optional locale and testOptions.
    let coll;
    try {
      coll = new Intl.Collator(testLocale, testCollOptions);

      let d1 = json['string1'];
      let d2 = json['string2'];

      const compared = coll.compare(d1, d2);
      let result = compared<= 0 ? true : false;
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
