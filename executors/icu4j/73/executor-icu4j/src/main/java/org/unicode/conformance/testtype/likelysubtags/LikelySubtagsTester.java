package org.unicode.conformance.testtype.likelysubtags;

import com.ibm.icu.util.ULocale;
import io.lacuna.bifurcan.Map;
import org.unicode.conformance.ExecutorUtils;
import org.unicode.conformance.testtype.ITestType;
import org.unicode.conformance.testtype.ITestTypeInputJson;
import org.unicode.conformance.testtype.ITestTypeOutputJson;

public class LikelySubtagsTester implements ITestType {

  public static LikelySubtagsTester INSTANCE = new LikelySubtagsTester();

  @Override
  public ITestTypeInputJson inputMapToJson(Map<String, String> inputMapData) {
    LikelySubtagsInputJson result = new LikelySubtagsInputJson();

    result.test_type = inputMapData.get("test_type", null);
    result.label = inputMapData.get("label", null);
    result.locale = inputMapData.get("locale", null);
    result.option = LikelySubtagsTestOption.valueOf(
        inputMapData.get("option", null)
    );

    return result;
  }

  @Override
  public ITestTypeOutputJson execute(ITestTypeInputJson inputJson) {
    LikelySubtagsInputJson input = (LikelySubtagsInputJson) inputJson;

    // partially construct output
    LikelySubtagsOutputJson output = new LikelySubtagsOutputJson();
    output.label = input.label;

    try {
      output.result = getLikelySubtagString(input);
    } catch (Exception e) {
      output.error = "error running test";
      output.error = e.getMessage();
      return output;
    }

    // If we get here, it's a pass/fail result (supported options and no runtime errors/exceptions)
    return output;
  }

  @Override
  public String formatOutputJson(ITestTypeOutputJson outputJson) {
    return ExecutorUtils.GSON.toJson((LikelySubtagsOutputJson) outputJson);
  }

  public String getLikelySubtagString(LikelySubtagsInputJson input) {
    String localeID = input.locale;
    ULocale locale = ULocale.forLanguageTag(localeID);

    LikelySubtagsTestOption option = input.option;

    switch (option) {
      case maximize:
        return ULocale.addLikelySubtags(locale).toLanguageTag();
      case minimize:
      case minimizeFavorRegion:
        return ULocale.minimizeSubtags(locale).toLanguageTag();
      case minimizeFavorScript:
        throw new UnsupportedOperationException(
            "Likely Subtags test option `minimizeFavorScript` not supported");
      default:
        throw new UnsupportedOperationException("Likely Subtags test option not supported");
    }
  }
}
