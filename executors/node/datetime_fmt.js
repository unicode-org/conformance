// Tests date/time formatting

// https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Intl/DateTimeFormat


module.exports = {
  testDateTimeFmt: function (json) {
    const label = json['label'];
    let locale = json['locale'];
    if (! locale) {
      locale = 'und';
    }

    let test_option;
    if (json['option']) {
      test_option = json['option'];
    }

    let return_json = {'label': label};

    // Get the date from input milliseconds.
    let test_date;
    if (json['input_millis']) {
      let millis = json['input_millis'];
      if (typeof millis == "string") {
        try {
          millis = parseFloat(millis);
        } catch (error) {
          return_json['error'] = 'DateTimeFormat converting millis:' + json['input_millis'] +  ': ' + error.message;
          return return_json;
        }
      }
      // Input in milliseconds since the epoch
      test_date = new Date(millis);
    }
    if (json['input_string']) {
      // Input in string to be parsed
      test_date = new Date(json['input_string']);
    }

    // Why does input of "0" give 2000-01-01?
    // And why does input of 0 give today?

    // TODO: Use the skeleton if provided

    let dt_formatter;
    try {
      dt_formatter = new Intl.DateTimeFormat(locale);
    } catch (error) {
      /* Something is wrong with the constructor */
      return_json['error'] = 'DateTimeFormat Constructor: ' + error.message;
      return return_json;
    }

    try {
      const formatted_dt = dt_formatter.format(test_date);
      return_json['result'] = formatted_dt;
    } catch (error) {
      return_json['unsupported'] = ': ' + error.message;
    }
    return return_json;
  }
}
