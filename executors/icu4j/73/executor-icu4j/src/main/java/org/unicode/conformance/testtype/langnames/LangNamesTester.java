package org.unicode.conformance.testtype.langnames;

import com.ibm.icu.util.ULocale;
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

    return result;
  }

  @Override
  public ITestTypeOutputJson execute(ITestTypeInputJson inputJson) {
    LangNamesInputJson input = (LangNamesInputJson) inputJson;

    // partially construct output
    LangNamesOutputJson output = new LangNamesOutputJson();
    output.label = input.label;

    try {
      String displayNameResult = getDisplayLanguageString(input);
      output.result = displayNameResult;
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
    return ExecutorUtils.GSON.toJson((LangNamesOutputJson) outputJson);
  }

  public String getDisplayLanguageString(LangNamesInputJson input) {
    String localeID = input.language_label;
    String displayLocaleID = input.locale_label;
    return ULocale.getDisplayNameWithDialect(localeID, displayLocaleID);
  }
}
