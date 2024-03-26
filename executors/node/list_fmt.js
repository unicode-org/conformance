// Tests Intl Locale for list formatting.

// https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Intl/Locale


module.exports = {
  testListFmt: function (json) {
    const label = json['label'];
    const locale = json['locale'];
    let test_options;
    if (json['options']) {
      test_options = json['options'];
    }
    let input_list;
    if (json['input_list']) {
      input_list = json['input_list'];
    }

    let return_json = {'label': label};
    let list_formatter;
    try {
      list_formatter = new Intl.ListFormat(locale, test_options);
    } catch (error) {
      /* Something is wrong with the constructor */
      return_json['error'] = 'CONSTRUCTOR: ' + error.message;
      return_json['options'] = test_options;
      return return_json;
    }

    try {
      let result = list_formatter.format(input_list);
      return_json['result'] = result;
    } catch (error) {
      return_json['error'] =
          'LIST FORMATTER UNKNOWN ERROR: ' + error.message;
    }
    return return_json;
  }
}
