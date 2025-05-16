// Tests Intl segmenter

// https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Intl/Segmenter


module.exports = {
  testSegmenter: function (json) {
    const label = json['label'];
    const locale = json['locale'];
    let options;
    let test_option;
    if (json['options']) {
      options = json['options'];
      let desired_granularity;
      if (options['granularity'] == 'grapheme_cluster') {
        desired_granularity = 'grapheme';
      } else {
        desired_granularity = options['granularity'];
      }
      test_option = desired_granularity;
    }

    let return_json = {'label': label};
    let segmented_result = [];
    try {
      segmenter = new Intl.Segmenter(locale, options);
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
