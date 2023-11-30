package org.unicode.conformance.testtype.collator;

import com.ibm.icu.text.Collator;
import com.ibm.icu.text.RuleBasedCollator;
import com.ibm.icu.util.ULocale;
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
  public ITestTypeInputJson parseInputJson(String inputLine) {
    return ExecutorUtils.GSON.fromJson(inputLine, CollatorInputJson.class);
  }

  @Override
  public ITestTypeOutputJson computeOutputJson(ITestTypeInputJson inputJson) throws Exception {
    CollatorInputJson input = (CollatorInputJson) inputJson;

    // partially construct output
    CollatorOutputJson output = new CollatorOutputJson();
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
  public String formatOutputJson(ITestTypeOutputJson outputJson) {
    return ExecutorUtils.GSON.toJson((CollatorOutputJson) outputJson);
  }

  //
  // helper fns
  //

  public Collator getCollatorForInput(CollatorInputJson input) throws Exception {
    RuleBasedCollator result = null;

    if (input.locale == null) {
      if (input.rules == null) {
        result = (RuleBasedCollator) RuleBasedCollator.getInstance();
      } else {
        result = new RuleBasedCollator(input.rules);
      }
    } else {
      ULocale locale = ULocale.forLanguageTag(input.locale);
      result = (RuleBasedCollator) RuleBasedCollator.getInstance(locale);
      if (input.rules != null) {
        String defaultRules = result.getRules();
        String newRules = defaultRules + input.rules;
        result = new RuleBasedCollator(newRules);
      }
    }

    if (input.ignorePunctuation) {
      result.setAlternateHandlingShifted(true);
    }

    return result;
  }
}
