// Tests Intl Locale for pluralrules.

// https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Intl/PluralRules

// TODO: Consider if a list of locales can be used.
module.exports = {
  testPluralRules: function (json) {
    const label = json['label'];
    let return_json = {'label': label};

    let locale = json['locale'].replace('_', '-');
    if (locale == 'root') {
      return_json['warning'] = 'locale <root> replaced with <und>';
      locale = 'und';
    }


    let test_options = {};
    let sample;

    if (json['sample']) {
      let raw_sample = json['sample'];
      if (raw_sample.indexOf('c') >= 0) {
        return {"label": label,
                "error" : "unusupported",
                "unsupported": "unsupported compact number",
                "error_detail": {'unsupported sample': json['sample']
                                }
               };
      }
      let index_of_decimal = raw_sample.indexOf('.');
      if (index_of_decimal >= 0) {
        sample = parseFloat(raw_sample);
        // Workaround for issue : https://github.com/tc39/ecma402/issues/397
        let num_fraction_digits = raw_sample.length - index_of_decimal -1;
        test_options['minimumFractionDigits'] = num_fraction_digits;
        test_options['maximumFractionDigits'] = num_fraction_digits;
      } else {
        sample = parseInt(raw_sample);
      }
    } else {
      return_json['error'] = 'Incomplete test: no sample included';
      return return_json;
    }

    let plural_type;
    if (json['type']) {
      plural_type = json['type'];
      test_options['type'] = plural_type;
    }

    let actual_locale;
    try {
      const supported_locales =
            Intl.PluralRules.supportedLocalesOf(locale, test_options);
      if (supported_locales.includes(locale)) {
        actual_locale = locale;
      } else {
        if (supported_locales) {
          actual_locale = supported_locales[0];
        }
        if (actual_locale == undefined) {
          // No, there's no good substitute.
          return {"label": label,
                  "error" : "unusupported",
                  "unsupported": "unsupported_locale",
                  "error_detail": {'unsupported_locale': locale,
                                   'supported_locals': supported_locales,
                                   'test_options': test_options
                                  }
                 };
        }
      }
    } catch (error) {
      /* Something is wrong with supporteLocalesOf */
      return_json['error'] = 'supporteLocalesOf: ' + error.message;
      return_json['options'] = test_options;
      return return_json;
    }

    let list_formatter;
    try {
     p_rules = new Intl.PluralRules(actual_locale, test_options);
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
    if (actual_locale != locale) {
      return_json['actual_locale'] = actual_locale;
    }
    return return_json;
  }
}
