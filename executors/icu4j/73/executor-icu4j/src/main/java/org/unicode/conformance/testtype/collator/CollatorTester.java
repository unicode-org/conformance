package org.unicode.conformance.testtype.collator;

import com.ibm.icu.text.Collator;
import com.ibm.icu.text.RuleBasedCollator;
import com.ibm.icu.util.ULocale;
import io.lacuna.bifurcan.IMap;
import io.lacuna.bifurcan.Map;
import java.util.Optional;
import org.unicode.conformance.ExecutorUtils;
import org.unicode.conformance.testtype.ITestType;
import org.unicode.conformance.testtype.ITestTypeInputJson;
import org.unicode.conformance.testtype.ITestTypeOutputJson;

public class CollatorTester implements ITestType {

  public static CollatorTester INSTANCE = new CollatorTester();

  //
  // overrides for ITestType
  //

  @Override
  public ITestTypeInputJson inputMapToJson(Map<String, Object> inputMapData) {
    CollatorInputJson result = new CollatorInputJson();
    result.test_type = (String) inputMapData.get("test_type", null);
    result.label = (String) inputMapData.get("label", null);

    // TODO: clean up after schema validation gets turned on at runtime
    result.s1 = (String) inputMapData.get("s1", null);
    if (result.s1 == null) {
      result.s1 = (String) inputMapData.get("string1", null);
    }

    // TODO: clean up after schema validation gets turned on at runtime
    result.s2 = (String) inputMapData.get("s2", null);
    if (result.s2 == null) {
      result.s2 = (String) inputMapData.get("string2", null);
    }

    result.locale = (String) inputMapData.get("locale", null);

    boolean ignorePunctuation = false;
    Optional<Object> ignorePunctuationStr = inputMapData.get("ignorePunctuation");
    try {
      if (ignorePunctuationStr.isPresent()) {
        ignorePunctuation = Boolean.parseBoolean((String) ignorePunctuationStr.get());
      }
    } catch (Exception e) {
      // do nothing, default is false
    }
    result.ignorePunctuation = ignorePunctuation;

    int line = 0;
    Optional<Object> lineStr = inputMapData.get("line");
    try {
      if (lineStr.isPresent()) {
        line = Integer.parseInt((String) lineStr.get());
      }
    } catch (Exception e) {
      // do nothing, default is 0
    }
    result.line = line;

    result.compare_type = (String) inputMapData.get("compare_type", null);
    result.test_description = (String) inputMapData.get("test_description", null);

    // TODO: implement this correctly recursively (either using APIs or else DIY)
    String[] attrs;
    Optional<Object> attrsString = inputMapData.get("attributes");
    if (attrsString.isPresent()) {
      attrs = new String[]{ (String) attrsString.get() };
    } else {
      attrs = new String[]{};
    }
    result.attributes = attrs;

    result.rules = (String) inputMapData.get("rules", null);
    result.compare_comment = (String) inputMapData.get("compare_comment", null);
    result.warning = (String) inputMapData.get("warning", null);

    return result;
  }

  @Override
  public ITestTypeOutputJson execute(ITestTypeInputJson inputJson) {
    CollatorInputJson input = (CollatorInputJson) inputJson;

    // partially construct output
    CollatorOutputJson output = (CollatorOutputJson) getDefaultOutputJson();
    output.label = input.label;
    output.s1 = input.s1;
    output.s2 = input.s2;

    // get and run collator based on options provided for test case input
    Collator coll = null;
    try {
      coll = getCollatorForInput(input);
    } catch (Exception e) {
      output.error = "unsupported";
      output.error_message = e.getMessage();
      return output;
    } finally {
      if (coll == null) {
        output.error = "unsupported";
        output.error_message = "Couldn't construct RuleBasedCollator with provided options";
        return output;
      }
    }

    try {
      int collResult = coll.compare(input.s1, input.s2);
      if (collResult > 0) {
        // failure
        output.result = false;
      } else {
        // success
        output.result = true;
      }
    } catch (Exception e) {
      output.error = "error running test";
      output.error = e.getMessage();
      return output;
    }

    // If we get here, it's a pass/fail result (supported options and no runtime errors/exceptions)
    return output;
  }

  @Override
  public ITestTypeOutputJson getDefaultOutputJson() {
    CollatorOutputJson output = new CollatorOutputJson();
    output.result = false;

    return output;
  }

  @Override
  public IMap<String, Object> convertOutputToMap(ITestTypeOutputJson outputJson) {
    CollatorOutputJson output = (CollatorOutputJson) outputJson;
    return new io.lacuna.bifurcan.Map<String,Object>()
        .put("label", output.label)
        .put("result", output.result)
        .put("s1", output.s1)
        .put("s2", output.s2);
  }

  @Override
  public String formatOutputJson(ITestTypeOutputJson outputJson) {
    return ExecutorUtils.GSON.toJson((CollatorOutputJson) outputJson);
  }

  //
  // helper fns
  //

  public Collator getCollatorForInput(CollatorInputJson input) {
    RuleBasedCollator result = null;

    if (input.locale == null) {
      if (input.rules == null) {
        result = (RuleBasedCollator) RuleBasedCollator.getInstance();
      } else {
        try {
          result = new RuleBasedCollator(input.rules);
        } catch (Exception e) {
          return null;
        }
      }
    } else {
      ULocale locale = ULocale.forLanguageTag(input.locale);
      result = (RuleBasedCollator) RuleBasedCollator.getInstance(locale);
      if (input.rules != null) {
        String defaultRules = result.getRules();
        String newRules = defaultRules + input.rules;
        try {
          result = new RuleBasedCollator(newRules);
        } catch (Exception e) {
          return null;
        }
      }
    }

    if (input.ignorePunctuation) {
      result.setAlternateHandlingShifted(true);
    }

    return result;
  }
}
