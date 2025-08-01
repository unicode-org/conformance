package org.unicode.conformance.testtype.collator;

import com.ibm.icu.impl.Utility;
import com.ibm.icu.text.Collator;
import com.ibm.icu.lang.UScript;
import com.ibm.icu.text.RuleBasedCollator;
import com.ibm.icu.util.ULocale;
import io.lacuna.bifurcan.IMap;
import io.lacuna.bifurcan.Map;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Optional;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
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

    HashMap<String, Integer> script_tags_map = new HashMap<String, Integer>();
    script_tags_map.put("digit", Collator.ReorderCodes.DIGIT);
    script_tags_map.put("space", Collator.ReorderCodes.SPACE);
    script_tags_map.put("symbol", Collator.ReorderCodes.SYMBOL);
    script_tags_map.put("punct", Collator.ReorderCodes.PUNCTUATION);
    script_tags_map.put("Latn", UScript.LATIN);
    script_tags_map.put("Goth", UScript.GOTHIC);
    script_tags_map.put("Grek", UScript.GREEK);
    script_tags_map.put("Hang", UScript.HANGUL);
    script_tags_map.put("Hani", UScript.HAN);
    script_tags_map.put("Hira", UScript.HIRAGANA);
    script_tags_map.put("Zzzz", UScript.UNKNOWN);

    result.s1 = Utility.unescape((String) inputMapData.get("s1", null));
    result.s2 = Utility.unescape((String) inputMapData.get("s2", null));

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
    result.strength = (String) inputMapData.get("strength", null);

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

    // A bunch of options
    String raw_rules = (String) inputMapData.get("rules", null);
    if (raw_rules != null) {
      result.rules = Utility.unescape(raw_rules);
    }

    result.compare_comment = (String) inputMapData.get("compare_comment", null);

    result.backwards = (String) inputMapData.get("backwards", null);
    result.alternate = (String) inputMapData.get("alternate", null);
    result.numeric = (String) inputMapData.get("numeric", null);

    // Compute reorder codes from input reorder_string
    String reorder_tag_string =  (String) inputMapData.get("reorder", null);
    if (reorder_tag_string != null) {
      // Split the string into tags
      String[] tags = reorder_tag_string.split(" ");
      // Create the list for setting reorder codes.
      result.reorder_codes = new int[tags.length];

      result.unrecognized_script_codes = "";

      // For each tag, look up the code and add to a list
      int index = 0;
      for (String tag : tags) {
        // For each tag, look up the code and add to a list of codes
        int script_code = script_tags_map.getOrDefault(tag, -1);
        if (script_code != -1) {
          result.reorder_codes[index] = script_code;
          index ++;
        } else {
          // TODO: Report that this script tag was not found.
          result.unrecognized_script_codes = result.unrecognized_script_codes + ", " + tag;
        }
      }
    }
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

    if (input.backwards != null) {
      // Special case
      output.actual_options = "Backwards reset of locale from " + input.locale;
      input.locale = "fr-CA";  // Reset the locale to be fr-CA
    }

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

    // Set the reorder codes if present
    if (input.reorder_codes != null && input.reorder_codes.length > 0) {
      coll.setReorderCodes(input.reorder_codes);
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
    RuleBasedCollator collator = null;

    ULocale locale = ULocale.ROOT;
    if (input.locale != null && !input.locale.equals("root")) {
      locale = new ULocale(input.locale);
    }

    collator = (RuleBasedCollator) Collator.getInstance(locale);
    if (input.rules != null) {
      // Convert it to a rule based collator.
      String defaultRules = collator.getRules();
      // Should we unescape the rules?
      String newRules = defaultRules + input.rules;
      try {
        collator = new RuleBasedCollator(newRules);
      } catch (Exception e) {
        return null;
      }
    }

    // ensure that ICU performs decomposition before collation in order to get proper collators,
    // per documentation: https://unicode-org.github.io/icu-docs/apidoc/dev/icu4j/com/ibm/icu/text/Collator.html
    collator.setDecomposition(Collator.CANONICAL_DECOMPOSITION);

    if (input.ignorePunctuation) {
      collator.setAlternateHandlingShifted(true);
    }

    if (input.alternate != null && input.alternate.equals("shifted")) {
      collator.setAlternateHandlingShifted(true);
    }

    if (input.numeric != null) {
      collator.setNumericCollation(true);
    }

    return collator;
  }
}
