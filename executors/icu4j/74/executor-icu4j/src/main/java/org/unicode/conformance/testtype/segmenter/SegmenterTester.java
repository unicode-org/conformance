package org.unicode.conformance.testtype.segmenter;

import static com.ibm.icu.text.BreakIterator.getCharacterInstance;
import static com.ibm.icu.text.BreakIterator.getWordInstance;
import static com.ibm.icu.text.BreakIterator.getLineInstance;
import static com.ibm.icu.text.BreakIterator.getSentenceInstance;

import com.ibm.icu.text.BreakIterator;
import com.ibm.icu.util.ULocale;
import io.lacuna.bifurcan.IMap;
import io.lacuna.bifurcan.Map;
import java.util.ArrayList;
import java.util.Collection;
import java.util.List;
import org.unicode.conformance.ExecutorUtils;
import org.unicode.conformance.testtype.ITestType;
import org.unicode.conformance.testtype.ITestTypeInputJson;
import org.unicode.conformance.testtype.ITestTypeOutputJson;


public class SegmenterTester implements ITestType {

  public static SegmenterTester INSTANCE = new SegmenterTester();

  @Override
  public ITestTypeInputJson inputMapToJson(Map<String, Object> inputMapData) {
    SegmenterInputJson result = new SegmenterInputJson();

    result.label = (String) inputMapData.get("label", null);
    result.locale = (String) inputMapData.get("locale", null);
    // The string to be segmented
    result.locale = (String) inputMapData.get("input", null);

    java.util.Map<String, Object> inputOptions =
        (java.util.Map<String, Object>) inputMapData.get("options", null);
    result.segmenterType = (String) inputOptions.get("granularity");

    result.inputString = (String) inputMapData.get("input", null);

    return result;
  }

  @Override
  public ITestTypeOutputJson execute(ITestTypeInputJson inputJson) {
    SegmenterInputJson input = (SegmenterInputJson) inputJson;

    // partially construct output
    SegmenterOutputJson output = (SegmenterOutputJson) getDefaultOutputJson();
    output.label = input.label;

    try {
      output.result = getSegmenterResult(input);
    } catch (Exception e) {
      output.error = e.getMessage();
      output.error_message = e.getMessage();
      return output;
    }

    // If we get here, it's a pass/fail result (supported options and no runtime errors/exceptions)
    return output;
  }

  @Override
  public ITestTypeOutputJson getDefaultOutputJson() {
    return new SegmenterOutputJson();
  }

  @Override
  public IMap<String, Object> convertOutputToMap(ITestTypeOutputJson outputJson) {
    SegmenterOutputJson output = (SegmenterOutputJson) outputJson;
    return new Map<String, Object>()
        .put("label", output.label)
        .put("result", output.result);
  }

  @Override
  public String formatOutputJson(ITestTypeOutputJson outputJson) {
    return ExecutorUtils.GSON.toJson((SegmenterOutputJson) outputJson);
  }

  public List<String> getSegmenterResult(SegmenterInputJson input) {
    ULocale locale = ULocale.forLanguageTag(input.locale);

    BreakIterator segmenter;
    switch (input.segmenterType) {
      default:
      case "grapheme_cluster":
        segmenter = getCharacterInstance(locale);
        break;
      case "word":
        segmenter = getWordInstance(locale);
        break;
      case "sentence":
        segmenter = getSentenceInstance(locale);
        break;
      case "line":
        segmenter = getLineInstance(locale);
        break;
    }
    segmenter.setText(input.inputString);
    // Segment the input, creating a list of strings as output.
    List<String> result = new ArrayList<>();
    int start_pos = segmenter.first();
    int end_pos = segmenter.next();

    while (end_pos != BreakIterator.DONE) {
      String target = input.inputString.substring(start_pos, end_pos);
      start_pos = end_pos;
      end_pos = segmenter.next();
      result.add(target);
    }

    return result;
  }
}
