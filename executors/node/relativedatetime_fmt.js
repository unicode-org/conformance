// Tests Intl Locale for relative date/time formatting.

// https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Intl/Locale


module.exports = {
  testRelativeDateTimeFmt: function (json) {
    const label = json['label'];
    const locale = json['locale'];
    let test_options;
    if (json['options']) {
      test_options = json['options'];
    }
    let unit;
    if (json['unit']) {
      unit = json['unit'];
    }
    let count;
    if (json['count']) {
      count = json['count'];
    }

    let return_json = {'label': label};
    let list_formatter;
    try {
      rdt_formatter = new Intl.RelativeTimeFormat(locale, test_options);
    } catch (error) {
      /* Something is wrong with the constructor */
      return_json['error'] = 'CONSTRUCTOR: ' + error.message;
      return_json['options'] = test_options;
      return return_json;
    }

    try {
      let result = rdt_formatter.format(count, unit);
      return_json['result'] = result;
    } catch (error) {
      return_json['error'] =
          'RELATIVE DATE TIME FORMATTER UNKNOWN ERROR: ' + error.message;
    }
    return return_json;
  }
}
