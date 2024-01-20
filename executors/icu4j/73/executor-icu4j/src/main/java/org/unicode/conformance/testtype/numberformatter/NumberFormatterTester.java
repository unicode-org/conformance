package org.unicode.conformance.testtype.numberformatter;

import com.ibm.icu.number.FormattedNumber;
import com.ibm.icu.number.NumberFormatter;
import com.ibm.icu.text.NumberingSystem;
import com.ibm.icu.util.ULocale;
import io.lacuna.bifurcan.Map;
import java.math.BigDecimal;
import java.util.HashMap;
import org.unicode.conformance.ExecutorUtils;
import org.unicode.conformance.testtype.ITestType;
import org.unicode.conformance.testtype.ITestTypeInputJson;
import org.unicode.conformance.testtype.ITestTypeOutputJson;

public class NumberFormatterTester implements ITestType {

  public static NumberFormatterTester INSTANCE = new NumberFormatterTester();

  @Override
  public ITestTypeInputJson inputMapToJson(Map<String, String> inputMapData) {
    NumberFormatterInputJson result = new NumberFormatterInputJson();

    result.label = inputMapData.get("label", null);
    result.input = inputMapData.get("input", null);
    result.locale = inputMapData.get("locale", null);
    result.pattern = inputMapData.get("pattern", null);
    result.skeleton = inputMapData.get("skeleton", null);
    result.op = inputMapData.get("op", null);

    String optionsStr = inputMapData.get("options", null);
    java.util.Map<String,String> parsedOptionsMap = ExecutorUtils.stringMapFromString(optionsStr);
    java.util.Map<NumberFormatterTestOptionKey, Object> options =
        new HashMap<>();
    options.put(
        NumberFormatterTestOptionKey.notation,
        parsedOptionsMap.get("notation"));
    options.put(
        NumberFormatterTestOptionKey.numberingSystem,
        parsedOptionsMap.get("numberingSystem"));
    options.put(
        NumberFormatterTestOptionKey.compactDisplay,
        CompactDisplayVal.getFromString(
            parsedOptionsMap.get("compactDisplay")));
    options.put(
        NumberFormatterTestOptionKey.currencySign,
        parsedOptionsMap.get("currencySign"));
    options.put(
        NumberFormatterTestOptionKey.signDisplay,
        SignDisplayVal.valueOf(
            parsedOptionsMap.get("signDisplay")));
    options.put(
        NumberFormatterTestOptionKey.style,
        StyleVal.valueOf(
            parsedOptionsMap.get("style")));
    options.put(
        NumberFormatterTestOptionKey.unit,
        parsedOptionsMap.get("unit"));
    options.put(
        NumberFormatterTestOptionKey.unitDisplay,
        UnitDisplayVal.getFromString(
            parsedOptionsMap.get("unitDisplay")));
    options.put(
        NumberFormatterTestOptionKey.currency,
        parsedOptionsMap.get("currency"));
    options.put(
        NumberFormatterTestOptionKey.currencyDisplay,
        CurrencyDisplayVal.valueOf(
            parsedOptionsMap.get("currencyDisplay")));
    options.put(
        NumberFormatterTestOptionKey.minimumFractionDigits,
        Integer.parseInt(
            parsedOptionsMap.get("minimumFractionDigits")));
    options.put(
        NumberFormatterTestOptionKey.maximumFractionDigits,
        Integer.parseInt(
            parsedOptionsMap.get("maximumFractionDigits")));
    options.put(
        NumberFormatterTestOptionKey.minimumIntegerDigits,
        Integer.parseInt(
            parsedOptionsMap.get("minimumIntegerDigits")));
    options.put(
        NumberFormatterTestOptionKey.minimumSignificantDigits,
        Integer.parseInt(
            parsedOptionsMap.get("minimumSignificantDigits")));
    options.put(
        NumberFormatterTestOptionKey.maximumSignificantDigits,
        Integer.parseInt(
            parsedOptionsMap.get("maximumSignificantDigits")));
    options.put(
        NumberFormatterTestOptionKey.nu,
        NuVal.valueOf(
            parsedOptionsMap.get("nu")));
    options.put(
        NumberFormatterTestOptionKey.roundingPriority,
        RoundingPriorityVal.valueOf(
            parsedOptionsMap.get("roundingPriority")));
    options.put(
        NumberFormatterTestOptionKey.roundingMode,
        RoundingModeVal.valueOf(
            parsedOptionsMap.get("roundingMode")));
    int roundingIncrement =
        Integer.parseInt(parsedOptionsMap.get("roundingIncrement"));
    assert RoundingIncrementUtil.isValidVal(roundingIncrement);
    options.put(
        NumberFormatterTestOptionKey.roundingIncrement,
        roundingIncrement
    );
    options.put(
        NumberFormatterTestOptionKey.trailingZeroDisplay,
        TrailingZeroDispalyVal.valueOf(
            parsedOptionsMap.get("trailingZeroDisplay")));
    options.put(
        NumberFormatterTestOptionKey.useGrouping,
        UseGroupingVal.getFromString(
            parsedOptionsMap.get("useGrouping")));
    result.options = options;

    return result;
  }

  @Override
  public ITestTypeOutputJson execute(ITestTypeInputJson inputJson) {
    NumberFormatterInputJson input = (NumberFormatterInputJson) inputJson;

    // partially construct output
    NumberFormatterOutputJson output = new NumberFormatterOutputJson();
    output.label = input.label;

    try {
      output.result = getFormattedNumber(input);
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
    return ExecutorUtils.GSON.toJson((NumberFormatterOutputJson) outputJson);
  }

  public String getFormattedNumber(NumberFormatterInputJson input) {
    BigDecimal inputVal = new BigDecimal(input.input);
    FormattedNumber fn =
        NumberFormatter.forSkeleton(input.skeleton)
            .locale(new ULocale(input.input))
            .format(inputVal);
    return fn.toString();
  }
}
