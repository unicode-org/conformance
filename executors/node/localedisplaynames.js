// Tests Intl class LangNames

module.exports = {

  testLocaleDisplayNames: function (json) {
    let locale = 'en';  // Default
    if (json['locale_label']) {
      // Fix to use dash, not underscore.
      locale = json['locale_label'].replace(/_/g, '-');
    }

    // Standard for this type of testing.
    let options = {type: 'language',
                   languageDisplay: 'standard',
                   style: 'long'};

    let label = json['label'];
    let input = json['language_label'].replace(/_/g, '-');
    let outputLine = {
      "label": json['label'],
      "locale_label": locale,
      "language_label": input,
    };

    try {
      const supported_locales =
            Intl.DisplayNames.supportedLocalesOf([locale]);
    } catch (error) {
      // Something wrong with the locale for this
      outputLine["error_detail"] = locale
      outputLine["error_type"] = 'unsupported locale';
      outputLine["unsupported"] = error.toString();
      return outputLine;
    }

    // Check the language to be formatted
    try {
      let language_label_locale = new Intl.Locale(input);
    } catch (error) {
      // Something wrong with the locale for this
      outputLine["error_detail"] = input;
      outputLine["error_type"] = 'Problem with language label';
      outputLine["unsupported"] = error.toString();
      outputLine["actual_options"] = JSON.stringify(options);
      return outputLine;
    }

    if (json['languageDisplay']) {
      options['languageDisplay'] = json['languageDisplay'];
    }

    let dn;
    try {
      dn = new Intl.DisplayNames([locale], options);
    } catch (error) {
      outputLine = {
        "error": error.toString(),
        "locale_label": locale,
        "error_detail": "Bad constructor for locale: " + locale + ' ' + options,
        "error_retry": false  // Do not repeat
      };
      if (error instanceof RangeError) {
        // The locale can't be handled for some reason!
        outputLine["error_type"] = 'unsupported';
        outputLine["unsupported"] = error.toString();
        outputLine["error_detail"] = locale;
        outputLine["actual_options"] = JSON.stringify(options);
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
                    "result": resultString,
                    "error_type": 'unsupported',
                    "unsupported": error.toString(),
                    "error_detail": input,
                    "actual_options": JSON.stringify(options)
                   };
    }
    return outputLine;
  }
}
