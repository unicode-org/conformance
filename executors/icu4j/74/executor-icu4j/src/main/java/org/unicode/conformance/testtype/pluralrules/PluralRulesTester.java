package org.unicode.conformance.testtype.pluralrules;

import com.ibm.icu.util.ULocale;
import com.ibm.icu.text.PluralRules.PluralType;
import com.ibm.icu.text.PluralRules;

import io.lacuna.bifurcan.IMap;
import io.lacuna.bifurcan.Map;

import java.util.Collection;

import java.util.HashMap;
import org.unicode.conformance.ExecutorUtils;
import org.unicode.conformance.testtype.ITestType;
import org.unicode.conformance.testtype.ITestTypeInputJson;
import org.unicode.conformance.testtype.ITestTypeOutputJson;
import org.unicode.conformance.testtype.pluralrules.PluralRulesInputJson;
import org.unicode.conformance.testtype.pluralrules.PluralRulesOutputJson;


public class PluralRulesTester implements ITestType {

  public static PluralRulesTester INSTANCE = new PluralRulesTester();

  public ITestTypeInputJson inputMapToJson(Map<String, Object> inputMapData) {
    PluralRulesInputJson result = new PluralRulesInputJson();

    result.label = (String) inputMapData.get("label", null);
    result.locale = (String) inputMapData.get("locale", null);

    result.plural_type = PluralRulesType.getFromString(
        "" + inputMapData.get("plural_type", null)
    );

    // Consider compact number format, too.
    String sample_string = (String) inputMapData.get("sample", null);
    // Convert this to a number.
    result.sample = Double.parseDouble(sample_string);

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
    PluralRules.PluralType plural_type;
    ULocale locale = ULocale.forLanguageTag(input.locale);

    switch (input.plural_type) {
      case ORDINAL:
        plural_type = PluralRules.PluralType.ORDINAL;
        break;
      default:
      case CARDINAL:
        plural_type = PluralRules.PluralType.CARDINAL;
        break;
    }

    PluralRules pl_rules = PluralRules.forLocale(locale, plural_type);

    return pl_rules.select(input.sample);
  }
}
