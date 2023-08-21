// Tests Intl Locale for minimize / maximize likely subtags.

// https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Intl/Locale


module.exports = {
  testLikelySubtags: function (json) {
    const label = json['label'];
    const locale = json['locale'];
    let test_option;
    if (json['option']) {
      test_option = json['option'];
    }

    let return_json = {'label': label};
    let intl_locale;
    try {
      intl_locale = new Intl.Locale(locale);
    } catch (error) {
      /* Something is wrong with the constructor */
      return_json['error'] = 'CONSTRUCTOR: ' + error.message;
      return return_json;
    }

    try {
      let result_locale;
      if (test_option === 'maximize') {
        result_locale = intl_locale.maximize().baseName;
      } else if (test_option === 'minimizeFavorScript' ||
                 test_option === 'minimize') {
        result_locale = intl_locale.minimize().baseName;
      } else if (test_option === 'minimizeFavorRegion') {
        result_locale = intl_locale.minimizeFavorRegion().baseName;
      } else {
        return_json['error'] = 'Unknown test option = ' + test_option;
      }
      return_json['result'] = result_locale;
    } catch (error) {
      return_json['unsupported'] = 'LIKELY_SUBTAGS UNKNOWN ERROR: ' + error.message;
    }
    return return_json;
  }
}
