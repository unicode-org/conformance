// Tests date/time formatting

// https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Intl/DateTimeFormat


module.exports = {
  testDateTimeFmt: function (json) {
    const label = json['label'];
    let locale = json['locale'];
    if (! locale) {
      locale = 'und';
    }

    let test_options = {};
    if (json['options']) {
      test_options = json['options'];
    }

    let return_json = {'label': label};

    // Get the date from input milliseconds.
    // Prefer milliseconds
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
    } else {
      // If no milliseconds given.
      if (json['input_string']) {
        // Input in string to be parsed
        test_date = new Date(json['input_string']);
      }
    }

    let dt_formatter;
    try {
      dt_formatter = new Intl.DateTimeFormat(locale, test_options);
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
