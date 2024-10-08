// Tests Intl class LangNames

module.exports = {

  testLocaleDisplayNames: function (json) {
    let locale = 'en';  // Default
    let options = {};
    if (json['locale_label']) {
      // Fix to use dash, not underscore.
      locale = json['locale_label'].replace(/_/g, '-');
    }

    // options = json['options'];
    options = {type: 'language', languageDisplay: 'standard'};
    let label = json['label'];
    let input = json['language_label'].replace(/_/g, '-');

    if (json['languageDisplay']) {
      // Fix to use dash, not underscore.
      options['languageDisplay'] = json['languageDisplay'];
    }

    let outputLine;

    let dn;
    try {
      dn = new Intl.DisplayNames([locale], options);
    } catch (error) {
      outputLine = {
        "error": error.toString(),
        "label": json['label'],
        "locale_label": locale,
        "language_label": input,
        "test_type": "display_names",
        "error_type": "unsupported",
        "error_retry": false  // Do not repeat
      };
      if (error instanceof RangeError) {
        // The locale can't be handled for some reason!
        outputLine["error_type"] = 'unsupported';
        outputLine["unsupported"] = error.toString();
        outputLine["error_detail"] = 'unsupported locale';
      }
      return outputLine;
    }

    let resultString;
    try {
      resultString = dn.of(input);
      outputLine = {"label": label,
                    "result": resultString
                   };
    } catch (error) {
      const error_string = error.toString();
      outputLine = {"label": json['label'],
                    "locale_label": locale,
                    "language_label": input,
                    "error": error_string,
                    "actual_options": options.toString(),
                   };
      outputLine["error_type"] = 'unsupported';
      outputLine["unsupported"] = error_string;
      if (error instanceof RangeError) {
        // The locale can't be handled for some reason!
        outputLine["error_detail"] = 'unsupported locale';
      }
    }
    return outputLine;
  }
}
