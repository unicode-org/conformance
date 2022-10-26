// Tests Intl class DisplayNames

module.exports = {

  testDisplayNames: function (json) {
    let locale = 'en';  // Default
    let options;
    if (json['locale']) {
      locale = json['locale'];
    }

    options = json['options'];
    let input = json['input'];

    let outputLine;
    try {
      const dn = new Intl.DisplayNames([locale], options);
      let resultString = dn.of(input);
      outputLine = {"label": json['label'],
                    "result": resultString
                   };
    } catch (error) {
      outputLine = {"label": json['label'],
                    "error": error
                   };
    }
    return outputLine;
  }
}
