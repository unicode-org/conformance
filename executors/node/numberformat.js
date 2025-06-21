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
  patternsToOptions.set("0005", {useGrouping: false,
                                 minimumIntegerDigits: 4,
                                 roundingIncrement: 5,
                                 maximumFractionDigits: 0,
                                 roundingPriority: "auto",
                                });

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
  "halfOdd",
  "unnecessary"
];


const unsupported_pattern_regex = [
  /0+0.#+E/,  // More than on signficant integer digit with scientific
  /^.0#*E/,     // Zero signficant integer digits with scientific
];

// TODO: supported options and allowed values should be indexed by Node version

module.exports = {

  testDecimalFormat: function(json, doLogInput) {
    const node_version = process.version;
    const label = json['label'];
    const skeleton = json['skeleton'];

    const pattern = json['pattern'];

    // The formatter can take a string as input, which is needed for very long
    // sets of digits. In some cases, the input data may be adjusted, e.g.,
    // for "percent" and "scale" options (see below).
    let input_as_string = json['input'];

    let options;
    let error = "unimplemented pattern";
    let unsupported_options = [];
    let return_json = {};

    if (pattern) {
      // only for checking unsupported patterns
      for (let item of unsupported_pattern_regex) {
        if (item.test(pattern)) {
          unsupported_options.push('pattern: ' + pattern);
          return {'label': label,
                  "unsupported": "unsupported_options",
                  "error_detail": {'unsupported_options': unsupported_options}
                 }
        }
      }
    }

    // Use options instead of pattern
    options = json['options'];
    const rounding = options['roundingMode'];
    // Default maximumFractionDigits and rounding modes are set in test generation
    if (! rounding) {
      options['roundingMode'] = 'halfEven';
    }
    // Check each option for implementation.

    // Handle percent - input value is the basis of the actual percent
    // expected, e.g., input='0.25' should be interpreted '0.25%'
    if (options['style'] && options['style'] === 'percent') {
      const input = parseFloat(input_as_string) / 100;
      input_as_string = input.toString();
    }

    // Handle scale in the skeleton
    let skeleton_terms;
    if (skeleton) {
      skeleton_terms = skeleton.split(" ");  // all the components

      const scale_regex = /scale\/(\d+\.\d*)/;
      const match_scale = skeleton.match(scale_regex);
      if (match_scale) {
        // Get the value and use it
        const scale_value = parseFloat(match_scale[1]);
        const input = parseFloat(input_as_string) * scale_value;;
        input_as_string = input.toString();
      }
    }

    // Check for "code":. Change to "currency":
    if (options['code']) {
      options['currency'] = options['code'];
      delete options['code'];
    }

    // Supported options depends on the nodejs version
    let version_supported_options;
    if (node_version >= first_v3_version) {
      version_supported_options =
          supported_options_by_version['v3'];
    } else {
      version_supported_options =
          supported_options_by_version['pre_v3'];
    }

    // Check for option items that are not supported
    for (let key in options) {
      if (!version_supported_options.includes(key)) {
        unsupported_options.push((key + ":" +  options[key]));
      }
    }

    // Check for skeleton terms that are not supported
    for (let skel_index in skeleton_terms) {
      const skel_term = skeleton_terms[skel_index];

      if (unsupported_skeleton_terms.includes(skel_term)) {
        unsupported_options.push(skel_term);
      }
    }

    if (unsupported_rounding_modes.includes(options['roundingMode'])) {
      unsupported_options.push(options['roundingMode']);
    }

    if (unsupported_options.length > 0) {
      return {'label': label,
              "unsupported": "unsupported_options",
              "error_detail": {'unsupported_options': unsupported_options}
             };
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
      // Use the string form, possibly adjusted.
      result = nf.format(input_as_string);

      // TODO: Catch unsupported units, e.g., furlongs.
      // Formatting as JSON
      resultString = result ? result : 'None';

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
