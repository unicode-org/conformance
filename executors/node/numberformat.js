// Tests NumberFormat and DecimalFormat classes

  let patternsToOptions = new Map();
  patternsToOptions.set("0.0", {minimumFractionDigits: 1});
  patternsToOptions.set("00", {minimumSignificantDigits: 1});
  patternsToOptions.set("0.0", {minimumFractionDigits: 1});
  patternsToOptions.set("@@@", {minimumSignificantDigits: 3});
  patternsToOptions.set("@@###", {minimumSignificantDigits: 2,
                                  maximumSignificantDigits: 5});
  patternsToOptions.set("0.0000E0", {notation: "scientific",
                                     minimunFractionDigits: 4});

module.exports = {
  decimalPatternToOptions: function(pattern, rounding) {
    // TODO: Fill in with options from
    let options = {};
    if (patternsToOptions.has(pattern)) {
      options = patternsToOptions.get(pattern);
    }
    if (rounding) {
      options['roundingMode'] = rounding;
    }
    return options;
  },

  testDecimalFormat: function(json) {
    const label = json['label'];

    const pattern = json['pattern'];
    const rounding = json['rounding'];
    const input = parseFloat(json['input']);

    let options;
    let error = "unimplemented pattern";

    // If options are in the JSON, use them...
    options = json['options'];
    if (!options) {
      try {
        options = this.decimalPatternToOptions(pattern, rounding);
      } catch (error) {
        // Some error - to return this message
        options = none;
      }
    }

    if (!options) {
      // Don't test, but return an error
      return {'label': label,
              'test_error': 'No options found',
             };
    }
    let testLocale = json['locale'];

    let nf;
    if (testLocale) {
      nf = new Intl.NumberFormat(testLocale, options);
    } else {
      nf = new Intl.NumberFormat(options);
    }
    let result = 'NOT IMPLEMENTED';
    result = nf.format(input);

    // Formatting as JSON
    resultString = result ? result : 'None'

    outputLine = {"label": json['label'],
                  "result": resultString,
                  "pattern": pattern
                 };
    return outputLine
  }

}
