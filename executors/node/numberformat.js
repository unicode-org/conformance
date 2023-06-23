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

const unsupported_skeleton_terms = [
  "scientific/+ee/sign-always",
  "decimal-always",
];

const unsupported_combinations = [
  {"unit": "furlong"}
];

// TODO: supported options should be indexed by Node version
// TODO: supported options and allowed values should be indexed by Node version

module.exports = {
  decimalPatternToOptions: function(pattern, rounding) {
    let options = {};

    if (patternsToOptions.has(pattern)) {
      options = patternsToOptions.get(pattern);
    }
    if (rounding) {
      options['roundingMode'] = rounding;
    }

    // Default unless overridden
    options["maximumFractionDigits"] = 6;  // Default
    return options;
  },

  testDecimalFormat: function(json, doLogInput) {
    const label = json['label'];
    const skeleton = json['skeleton'];

    const pattern = json['pattern'];
    const rounding = json['rounding'];
    let input = parseFloat(json['input']);  // May be changed with some options

    let options;
    let error = "unimplemented pattern";
    let unsupported_options = [];
    let return_json = {};

    // If options are in the JSON, use them...
    options = json['options'];
    if (!options) {
      try {
        options = this.decimalPatternToOptions(pattern, rounding);
      } catch (error) {
        // Some error - to return this message
        return_json['error'] = "Can't convert pattern";
        return_json['label'] = label;
        options = none;
      }
    } else {
      // Check each option for implementation.

      // Handle percent - input value is the basis of the actual percent
      // expected, e.g., input='0.25' should be interpreted '0.25%'
      if (options['style'] && options['style'] === 'percent') {
        input = input / 100.0;
      }

      // Handle scale in the skeleton
      let skeleton_terms;
      if (skeleton) {
        skeleton_terms = skeleton.split(" ");  // all the components
        if (doLogInput > 0) {
          console.log("# SKEL: " + skeleton_terms);
        }
        const scale_regex = /scale\/(\d+\.\d*)/;
        const match_scale = skeleton.match(scale_regex);
        if (match_scale) {
          // Get the value and use it
          const scale_value = parseFloat(match_scale[1]);
          input = input * scale_value;
        }

        //
      }

      // Check for "code":. Change to "currency":
      if (options["code"]) {
        options["currency"] = options["code"];
        delete options["code"];
      }

      // Check for option items that are not supported
      for (let key in options) {
        if (!all_supported_options.includes(key)) {
          unsupported_options.push((key + ":" +  options[key]));
        }
      }

      // Check for skelection terms that are not supported
      for (let skel_index in skeleton_terms) {
        const skel_term = skeleton_terms[skel_index];
        if (doLogInput > 0) {
          console.log("# SKEL_TERM: " + skel_term);
        }
        if (unsupported_skeleton_terms.includes(skel_term)) {
          unsupported_options.push(skel_term);
          if (doLogInput > 0) {
            console.log("# UNSUPPORTED SKEL_TERM: " + skel_term);
          }
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

      // TODO: Catch unsupported units, e.g., furlongs.
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
    return outputLine;
  }
}
