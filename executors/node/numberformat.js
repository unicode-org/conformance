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

let debug = 1;

// List of supported options. If unexpected options are seen, return
// "unsupported" rather than an error.
// Use array.includes(optionX) to check.
// TODO: Should this also include the values for each option?
const all_supported_options = [
  "compactDisplay",
  "currency",
  "currencyDisplay",
  "currencySign",
  "localeMatcher",
  "notation",
  "numberingSystem",
  "signDisplay",
  "style",
  "unit",
  "unitDisplay",
  "useGrouping",
  "roundingMode",
  "roundingPriority",
  "roudingIncrement",
  "trailingZeroDisplay",
  "minimumIntegerDigits",
  "minimumFractionDigits",
  "maximumFractionDigits",
  "minimumSignificantDigits",
  "maximumSignificantDigits"
];

module.exports = {
  decimalPatternToOptions: function(pattern, rounding) {
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
    const skeleton = json['skeleton'];

    console.log("# LABEL = " + label + " " + JSON.stringify(json));
    const pattern = json['pattern'];
    const rounding = json['rounding'];
    const input = parseFloat(json['input']);

    let options;
    let error = "unimplemented pattern";
    let unsupported_options = [];
    let return_json = {};

    // If options are in the JSON, use them...
    options = json['options'];
    console.log("#    OPTIONS = " + options);
    if (!options) {
      console.log("#   NOT OPTIONS " + JSON.stringify(options));
      try {
        options = this.decimalPatternToOptions(pattern, rounding);
      } catch (error) {
        // Some error - to return this message
        return_json['error'] = "Can't convert pattern";
        return_json['label'] = label;
        options = none;
      }
    } else {
      console.log("#OPTIONS: " + options);
      // Check each option for implementation.
      // Check for "code":. Change to "currency":
      if (options["code"]) {
        options["currency"] = options["code"];
        delete options["code"];
        console.log("Removing CODE " + label)
        console.log(" Giving options: " + options);
      }
      // Fix "SignDisplay" --> "signDisplay"
      if ("SignDisplay" in options) {
        options["signDisplay"] = options["SignDisplay"];
        delete options["SignDisplay"];
        console.log("Removing SignDisplay " + label)
        console.log(" Giving options: " + options);
      }
      for (key in options) {
        if (!all_supported_options.includes(key)) {
          unsupported_options.push((key + ":" +  options[key]));
        }
      }
      if (unsupported_options.length > 0) {
        return {'label': label,
                "unsupported": "unsupported_options",
                "error_detail": {'unsupported_options': unsupported_options}
               };
      }
    }

    if (!options) {
      // Don't test, but return an error
      return {'label': label,
              'error': 'No options found',
             };
    }
    let testLocale = json['locale'];

    let nf;
    try {
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
                   };
    } catch (error) {
      // Handle type of the error
      outputLine = {"label": json['label'],
                    "error": "formatting error",
                   };
      if (error instanceof RangeError) {
        outputLine["error_detail"] =  error.message;
      }
    }
    return outputLine
  }
}
