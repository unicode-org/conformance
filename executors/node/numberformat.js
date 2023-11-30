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
const all_supported_options_pre_v3 = [
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
  "roundingIncrement",
  "trailingZeroDisplay",
  "minimumIntegerDigits",
  "minimumFractionDigits",
  "maximumFractionDigits",
  "minimumSignificantDigits",
  "maximumSignificantDigits"
];

// The nodejs version that first supported advance rounding options
const first_v3_version = 'v20.1.0';

// Use this
const supported_options_by_version = {
  "v3": [
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
  "roundingIncrement",
  "trailingZeroDisplay",
  "minimumIntegerDigits",
  "minimumFractionDigits",
  "maximumFractionDigits",
  "minimumSignificantDigits",
  "maximumSignificantDigits"
  ],
  "pre_v3": [
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
  "minimumIntegerDigits",
  "minimumFractionDigits",
  "maximumFractionDigits",
  "minimumSignificantDigits",
  "maximumSignificantDigits"
  ]
  // TODO: Add older version support.
};

// TODO: usegrouping only supports boolean before V3.
// After V3, "min2", "auto", "always", and undefined are accepted

const unsupported_skeleton_terms = [
  "scientific/+ee/sign-always",
  "decimal-always",
];

const unsupported_combinations = [
  {"unit": "furlong"}
];


const unsupported_rounding_modes = [
  "unnecessary"
];

// TODO: supported options and allowed values should be indexed by Node version

module.exports = {
  decimalPatternToOptions: function(pattern, rounding) {
    let options = {};

    if (patternsToOptions.has(pattern)) {
      options = patternsToOptions.get(pattern);
    }
    if (rounding) {
      options['roundingMode'] = rounding;
    } else {
      // Default expected by the data
      options['roundingMode'] = 'halfEven';
    }
    return options;
  },

  testDecimalFormat: function(json, doLogInput) {
    const node_version = process.version;
    const label = json['label'];
    const skeleton = json['skeleton'];

    const pattern = json['pattern'];
    const rounding = json['roundingMode'];
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
      // Default maximumFractionDigits and rounding modes are set in test generation
      let roundingMode = options['roundingMode'];
      if (! roundingMode) {
        // Tests assume halfEven.
        roundingMode = options['roundingMode'] = 'halfEven';
      }

      // Check each option for implementation.

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
      if (options['code']) {
        options['currency'] = options['code'];
        delete options['code'];
      }

      // Supported options depends on the nodejs version
      if (doLogInput > 0) {
        console.log("#NNNN " + node_version);
      }
      let version_supported_options;
      if (node_version >= first_v3_version) {
        if (doLogInput > 0) {
          console.log("#V3 !!!! " + node_version);
        }
        version_supported_options =
            supported_options_by_version['v3'];
      } else {
        if (doLogInput > 0) {
          console.log("#pre_v3 !!!! " + node_version);
        }
        version_supported_options =
        supported_options_by_version['pre_v3'];
      }
      if (doLogInput > 0) {
        console.log("#NNNN " + version_supported_options);
      }
      // Check for option items that are not supported
      for (let key in options) {
        if (!version_supported_options.includes(key)) {
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

      if (unsupported_rounding_modes.includes(roundingMode)) {
        unsupported_options.push(roundingMode);
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
        nf = new Intl.NumberFormat('und', options);
      }

      let result = 'NOT IMPLEMENTED';
      result = nf.format(input);

      // TODO: Catch unsupported units, e.g., furlongs.
      // Formatting as JSON
      resultString = result ? result : 'None'



      outputLine = {"label": json['label'],
                    "result": resultString,
                    "actual_options": options
                   };
    } catch (error) {
      if (error.message.includes('furlong')) {
        // This is a special kind of unsupported.
        return {'label': label,
                "unsupported": "unsupported_options",
                "error_detail": {'unsupported_options': error.message}
               };
      }
      // Handle type of the error
      outputLine = {"label": json['label'],
                    "error": "formatting error",
                    'error_detail': error.message
                   };
      if (error instanceof RangeError) {
        outputLine['error_detail'] =  error.message;
        outputLine['actual_options'] = options
      }
    }
    return outputLine;
  }
}
