package org.unicode.conformance.testtype.likelysubtags;

import com.ibm.icu.util.ULocale;
import io.lacuna.bifurcan.IMap;
import io.lacuna.bifurcan.Map;
import org.unicode.conformance.ExecutorUtils;
import org.unicode.conformance.testtype.ITestType;
import org.unicode.conformance.testtype.ITestTypeInputJson;
import org.unicode.conformance.testtype.ITestTypeOutputJson;

public class LikelySubtagsTester implements ITestType {

  public static LikelySubtagsTester INSTANCE = new LikelySubtagsTester();

  @Override
  public ITestTypeInputJson inputMapToJson(Map<String, Object> inputMapData) {
    LikelySubtagsInputJson result = new LikelySubtagsInputJson();

    result.test_type = (String) inputMapData.get("test_type", null);
    result.label = (String) inputMapData.get("label", null);
    result.locale = (String) inputMapData.get("locale", null);
    result.option = LikelySubtagsTestOption.valueOf(
        (String) inputMapData.get("option", null)
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
      output.error_type = "unsupported";
      output.unsupported = e.getMessage();
      output.error_detail = e.getMessage();
      return output;
    }

    // If we get here, it's a pass/fail result (supported options and no runtime errors/exceptions)
    return output;
  }

  @Override
  public ITestTypeOutputJson getDefaultOutputJson() {
    return new LikelySubtagsOutputJson();
  }

  @Override
  public IMap<String, Object> convertOutputToMap(ITestTypeOutputJson outputJson) {
    LikelySubtagsOutputJson output = (LikelySubtagsOutputJson) outputJson;
    return new io.lacuna.bifurcan.Map<String,Object>()
        .put("label", output.label)
        .put("locale", output.locale)
        .put("result", output.result)
        .put("option", output.option);
  }

  @Override
  public String formatOutputJson(ITestTypeOutputJson outputJson) {
    return ExecutorUtils.GSON.toJson((LikelySubtagsOutputJson) outputJson);
  }

  public String getLikelySubtagString(LikelySubtagsInputJson input) {
    String localeID = input.locale;
    ULocale locale = ULocale.forLanguageTag(localeID);

    LikelySubtagsTestOption option = input.option;

    String lang_code = locale.getLanguage();
    if ((lang_code.compareTo("qaa") >= 0) && (lang_code.compareTo("qtz") <= 0)) {
      return "FAIL";  // This is an expected failure.
    }

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
