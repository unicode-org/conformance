// Tests Intl class LangNames

module.exports = {

  testLangNames: function (json) {
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

    let outputLine;
    //console.log("langnames input: " + input +
    //            " options: " + JSON.stringify(options) + " locale " + locale);

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
      return outputLine;
    }

    let resultString;
    try {
      resultString = dn.of(input);
      outputLine = {"label": label,
                    "result": resultString
                   };
    } catch (error) {
      //console.log("LangName problem: input = " + input + ", error = " + error);
      outputLine = {"label": json['label'],
                    "locale_label": locale,
                    "language_label": input,
                    "result": resultString,
                    "error": error.toString()
                   };
    }
    return outputLine;
  }
}
