// Tests Intl segmenter

// https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Intl/Segmenter

const supported_options = ['grapheme', 'word', 'sentence'];

module.exports = {
  testSegmenter: function (json) {
    const label = json['label'];
    const locale = json['locale'];
    let options;
    let ecma_intl_test_option;
    if (json['options']) {
      options = json['options'];
      ecma_intl_test_option = options['granularity'];
      if (options['granularity'] == 'grapheme_cluster') {
        // Change to use ECMAScript's enum.
        ecma_intl_test_option = 'grapheme';
      }
    }

    let return_json = {'label': label};
    if (!supported_options.includes(ecma_intl_test_option)) {
      // Not supported
      return_json['unsupported'] = 'granularity';
      return_json['error_detail'] = ecma_intl_test_option;
      return return_json;
    }
    let segmented_result = [];
    try {
      segmenter = new Intl.Segmenter(locale, {'granularity': ecma_intl_test_option});
    } catch (error) {
      /* Something is wrong with the constructor */
      return_json['error'] = 'CONSTRUCTOR: ' + error.message;
      return return_json;
    }

    let input;
    try {
      input = json['input'];
    } catch (error) {
      return_json['error'] = 'INPUT ERROR: ' + error.message;
      return return_json;
    }

    try {
      // Iterate through the results until error
      const iterator = segmenter.segment(input)[Symbol.iterator]();
      let seg_item = iterator.next();
      while (! seg_item.done) {
        segmented_result.push(seg_item.value.segment);
        seg_item = iterator.next();
      }
    } catch (error) {
      return_json['unsupported'] = 'SEGMENTER UNKNOWN ERROR: ' + error.message;
    }
    return_json['result'] = segmented_result;
    return return_json;


  }
}
