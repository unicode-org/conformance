package org.unicode.conformance.testtype.pluralrules;

import com.ibm.icu.util.ULocale;
import com.ibm.icu.text.PluralRules;

import io.lacuna.bifurcan.IMap;
import io.lacuna.bifurcan.Map;

import org.unicode.conformance.ExecutorUtils;
import org.unicode.conformance.testtype.ITestType;
import org.unicode.conformance.testtype.ITestTypeInputJson;
import org.unicode.conformance.testtype.ITestTypeOutputJson;


public class PluralRulesTester implements ITestType {

  public static PluralRulesTester INSTANCE = new PluralRulesTester();

  public ITestTypeInputJson inputMapToJson(Map<String, Object> inputMapData) {
    PluralRulesInputJson result = new PluralRulesInputJson();

    result.label = (String) inputMapData.get("label", null);
    result.locale = (String) inputMapData.get("locale", null);

    result.pluralType = PluralRulesType.getFromString(
        "" + inputMapData.get("plural_type", null)
    );

    // Consider compact number format, too.
    String sampleString = (String) inputMapData.get("sample", null);
    // Convert this to a number.
    result.sample = Double.parseDouble(sampleString);

    return result;
  }

  @Override
  public ITestTypeOutputJson execute(ITestTypeInputJson inputJson) {
    PluralRulesInputJson input = (PluralRulesInputJson) inputJson;

    // partially construct output
    PluralRulesOutputJson output = (PluralRulesOutputJson) getDefaultOutputJson();
    output.label = input.label;

    try {
      output.result = getPluralRulesResultString(input);
    } catch (Exception e) {
      output.error = e.getMessage();
      output.error_message = e.getMessage();
      return output;
    }

    // If we get here, it's a pass/fail result (supported options and no runtime errors/exceptions)
    return output;
  }

  public ITestTypeOutputJson getDefaultOutputJson() {
    return new PluralRulesOutputJson();
  }

  @Override
  public String formatOutputJson(ITestTypeOutputJson outputJson) {
    return ExecutorUtils.GSON.toJson((PluralRulesOutputJson) outputJson);
  }

  @Override
  public IMap<String, Object> convertOutputToMap(ITestTypeOutputJson outputJson) {
    PluralRulesOutputJson output = (PluralRulesOutputJson) outputJson;
    return new io.lacuna.bifurcan.Map<String, Object>()
        .put("label", output.label)
        .put("result", output.result);
  }

  public String getPluralRulesResultString(PluralRulesInputJson input) {
    PluralRules.PluralType pluralType;
    ULocale locale = ULocale.forLanguageTag(input.locale);

    switch (input.pluralType) {
      case ORDINAL:
        pluralType = PluralRules.PluralType.ORDINAL;
        break;
      default:
      case CARDINAL:
        pluralType = PluralRules.PluralType.CARDINAL;
        break;
    }

    PluralRules pluralRules = PluralRules.forLocale(locale, pluralType);

    return pluralRules.select(input.sample);
  }
}
