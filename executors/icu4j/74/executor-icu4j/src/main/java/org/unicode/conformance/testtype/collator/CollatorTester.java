package org.unicode.conformance.testtype.collator;

import com.ibm.icu.text.Collator;
import com.ibm.icu.text.RuleBasedCollator;
import com.ibm.icu.util.ULocale;
import io.lacuna.bifurcan.IMap;
import io.lacuna.bifurcan.Map;
import java.util.ArrayList;
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
    result.strength = (String) inputMapData.get("strength", null);

    result.ignorePunctuation = (boolean) inputMapData.get("ignorePunctuation", false);
    result.line = (int) ((double) inputMapData.get("line", 0.0));

    // Resolve "&lt;"
    result.compare_type = (String) inputMapData.get("compare_type", null);
    if (result.compare_type != null && ! result.compare_type.equals("") && result.compare_type.length() > 4) {
      String first_part = result.compare_type.substring(0,4);
      if (first_part.equals("&lt;")) {
        String next_part = result.compare_type.substring(4,5);
        result.compare_type = "<" + next_part;
      }
    }
    result.test_description = (String) inputMapData.get("test_description", null);

    // TODO: implement this correctly recursively (either using APIs or else DIY)
    ArrayList<String> attrs;
    Optional<Object> attrsListOpt = inputMapData.get("attributes");
    if (attrsListOpt.isPresent()) {
      attrs = (ArrayList<String>) attrsListOpt.get();
    } else {
      attrs = new ArrayList<>();
    }
    result.attributes = attrs;

    result.rules = (String) inputMapData.get("rules", null);
    result.compare_comment = (String) inputMapData.get("compare_comment", null);
    result.warning = (String) inputMapData.get("warning", null);

    result.backwards = (String) inputMapData.get("backwards", null);

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

    // Use the compare_type field to set the strength of collation test.
    if (input.strength != null) {
      if (input.strength.equals("identical")) {
        coll.setStrength(Collator.IDENTICAL);
      } else
      if (input.strength.equals("primary")) {
        coll.setStrength(Collator.PRIMARY);
      } else
      if (input.strength.equals("secondary")) {
        coll.setStrength(Collator.SECONDARY);
      } else
      if (input.strength.equals("tertiary")) {
        coll.setStrength(Collator.TERTIARY);
      } else
      if (input.strength.equals("quaternary")) {
        coll.setStrength(Collator.QUATERNARY);
      }
    }

    try {
      int collResult = coll.compare(input.s1, input.s2);
      // TODO! Use compare_type to check for <= or ==.
      if (collResult > 0) {
        // failure
        output.result = false;
      } else {
        // success
        output.result = true;
      }
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

    // Special case: Reset the locale to fr-CA in special case of backwards diacritics
    if (input.backwards != null && input.backwards.equals("on")) {
      input.locale = "fr-CA";
    }

    if (input.locale == null || input.locale == "root") {
      // Review this logic
      if (input.rules == null) {
        result = (RuleBasedCollator) Collator.getInstance(ULocale.ROOT);
      } else {
        try {
          result = new RuleBasedCollator(input.rules);
        } catch (Exception e) {
          return null;
        }
      }
    } else {
      ULocale locale = new ULocale(input.locale);
      result = (RuleBasedCollator) Collator.getInstance(locale);
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

    // ensure that ICU performs decomposition before collation in order to get proper results,
    // per documentation: https://unicode-org.github.io/icu-docs/apidoc/dev/icu4j/com/ibm/icu/text/Collator.html
    result.setDecomposition(Collator.CANONICAL_DECOMPOSITION);

    if (input.ignorePunctuation) {
      result.setAlternateHandlingShifted(true);
    }

    return result;
  }
}
