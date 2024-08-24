package org.unicode.conformance.testtype.langnames;

import com.ibm.icu.util.ULocale;
import io.lacuna.bifurcan.IMap;
import io.lacuna.bifurcan.Map;
import org.unicode.conformance.ExecutorUtils;
import org.unicode.conformance.testtype.ITestType;
import org.unicode.conformance.testtype.ITestTypeInputJson;
import org.unicode.conformance.testtype.ITestTypeOutputJson;
import org.unicode.conformance.testtype.collator.CollatorInputJson;
import org.unicode.conformance.testtype.collator.CollatorOutputJson;

public class LangNamesTester implements ITestType {

  public static LangNamesTester INSTANCE = new LangNamesTester();

  @Override
  public ITestTypeInputJson inputMapToJson(Map<String, Object> inputMapData) {
    LangNamesInputJson result = new LangNamesInputJson();

    result.test_type = (String) inputMapData.get("test_type", null);
    result.label = (String) inputMapData.get("label", null);

    result.language_label = (String) inputMapData.get("language_label", null);
    result.locale_label = (String) inputMapData.get("locale_label", null);

    String lang_display_string = (String) inputMapData.get("languageDisplay", null);
    result.language_display = LangNamesDisplayOptions.getFromString(lang_display_string);

    return result;
  }

  @Override
  public ITestTypeOutputJson execute(ITestTypeInputJson inputJson) {
    LangNamesInputJson input = (LangNamesInputJson) inputJson;

    // partially construct output
    LangNamesOutputJson output = (LangNamesOutputJson) getDefaultOutputJson();
    output.label = input.label;

    try {
      String displayNameResult = getDisplayLanguageString(input);
      output.result = displayNameResult;
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
    return new LangNamesOutputJson();
  }

  @Override
  public IMap<String, Object> convertOutputToMap(ITestTypeOutputJson outputJson) {
    LangNamesOutputJson output = (LangNamesOutputJson) outputJson;
    return new io.lacuna.bifurcan.Map<String,Object>()
        .put("label", output.label)
        .put("result", output.result)
        .put("language_label", output.language_label)
        .put("local_label", output.locale_label);
  }

  @Override
  public String formatOutputJson(ITestTypeOutputJson outputJson) {
    return ExecutorUtils.GSON.toJson((LangNamesOutputJson) outputJson);
  }

  public String getDisplayLanguageString(LangNamesInputJson input) {
    String localeID = input.language_label;
    String displayLocaleID = input.locale_label;
    if (input.language_display == LangNamesDisplayOptions.STANDARD) {
      return ULocale.getDisplayName(localeID, displayLocaleID);
    } else {
      return ULocale.getDisplayNameWithDialect(localeID, displayLocaleID);
    }
  }
}
