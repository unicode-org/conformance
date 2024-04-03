// Tests Intl Locale for pluralrules.

// https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Intl/Locale


// TODO: Consider if a list of locales can be used.
module.exports = {
  testPluralRules: function (json) {
    const label = json['label'];
    const locale = json['locale'];

    let return_json = {'label': label};


    let test_options = {};
    let sample;
    if (json['sample']) {
      sample = Number(json['sample']);  // Convert to a number
    }
    let plural_type;
    if (json['type']) {
      plural_type = json['plural_type'];
      test_options['type'] = plural_type;
    }

    const supported_locales =
          Intl.PluralRules.supportedLocalesOf(locale, test_options);
    console.log("supported: ", supported_locales);
    if (!supported_locales.includes(locale)) {
      return {"label": label,
              "unsupported": "unsupported_locale",
              "error_detail": {'unsupported_locale': locale}
             };
    }

    let list_formatter;
    try {
      p_rules = new Intl.PluralRules(locale, test_options);
    } catch (error) {
      /* Something is wrong with the constructor */
      return_json['error'] = 'CONSTRUCTOR: ' + error.message;
      return_json['options'] = test_options;
      return return_json;
    }

    try {
      let result = p_rules.select(sample);
      return_json['result'] = result;
    } catch (error) {
      return_json['error'] =
          'PLURAL RULES UNKNOWN ERROR: ' + error.message;
    }
    return return_json;
  }
}
