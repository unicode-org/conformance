// Tests date/time formatting

// https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Intl/DateTimeFormat


module.exports = {
  testDateTimeFmt: function (json) {
    const label = json['label'];
    let locale = json['locale'];
    const intl_locale = new Intl.Locale(locale);
    if (! locale) {
      locale = 'und';
    }

    let test_options = {};
    if (json['options']) {
      test_options = json['options'];
    }

    let calendar;
    try {
      calendar = test_options['calendar'];
    } catch {
      calendar = null;
    }
    let return_json = {'label': label};

    let timezone;
    try {
       timezone = test_options['time_zone'];
    } catch {
      timezone = options['timeZone'] = 'UTC';
    }
    // Get the date from input milliseconds.
    // Prefer milliseconds
    let iso_date;
    let test_date;

    // Parse the input string as a date.
    if (json['input_string']) {
      iso_date = json['input_string'];
      // Remove anything starting with "["
      let option_start = iso_date.indexOf('[');
      let test_date_string;
      if (option_start >= 0) {
        // TODO: !! Get the timezone and calendar from the iso_date string.
        test_date_string = iso_date.substring(0, option_start);
      } else {
        test_date_string = iso_date;
      }
      console.log('test_date_string %s', test_date_string);
      test_date = new Date(test_date_string);
    }

    try {
      if (calendar) {
        const supported_calendars = intl_locale.calendars;
        // Check if the calendar system is supported in this locale.
        // If not, skip the test.
        if ( !supported_calendars.includes(calendar)) {
          return_json['unsupported'] = ': ' + error.message;
          return return_json;
        }
      }
    } catch(error) {
      // This is not yet supported.
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
      return_json['actual_options'] = test_options;
      return_json['result'] = formatted_dt;
    } catch (error) {
      return_json['unsupported'] = ': ' + error.message;
    }
    return return_json;
  }
}
