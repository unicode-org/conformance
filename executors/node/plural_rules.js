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
      if (raw_sample.indexOf('.') >= 0) {
        sample = parseFloat(raw_sample);
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

    try {
      const supported_locales =
            Intl.PluralRules.supportedLocalesOf(locale, test_options);

      if (!supported_locales.includes(locale)) {

        return {"label": label,
                "error" : "unusupported",
                "unsupported": "unsupported_locale",
                "error_detail": {'unsupported_locale': locale,
                                 'supported_locals': supported_locales,
                                 'test_options': test_options
                                }
               };
      }
    } catch (error) {
      // Ignore for now.
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
