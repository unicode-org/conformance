package org.unicode.conformance.testtype.numberformatter;

import com.ibm.icu.number.FormattedNumber;
import com.ibm.icu.number.LocalizedNumberFormatter;
import com.ibm.icu.number.NumberFormatter;
import com.ibm.icu.util.Currency;
import com.ibm.icu.util.ULocale;
import io.lacuna.bifurcan.IMap;
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
  public ITestTypeInputJson inputMapToJson(Map<String, Object> inputMapData) {
    NumberFormatterInputJson result = new NumberFormatterInputJson();

    result.label = (String) inputMapData.get("label", null);
    result.input = (String) inputMapData.get("input", null);
    result.locale = (String) inputMapData.get("locale", null);
    result.pattern = (String) inputMapData.get("pattern", null);
    result.skeleton = (String) inputMapData.get("skeleton", null);
    result.op = (String) inputMapData.get("op", null);

    java.util.Map<String,Object> parsedOptionsMap =
        (java.util.Map<String,Object>) inputMapData.get("options", null);
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
            (String) parsedOptionsMap.get("compactDisplay")));
    options.put(
        NumberFormatterTestOptionKey.currencySign,
        parsedOptionsMap.get("currencySign"));
    options.put(
        NumberFormatterTestOptionKey.signDisplay,
        SignDisplayVal.getFromString(
            (String) parsedOptionsMap.get("signDisplay")));
    options.put(
        NumberFormatterTestOptionKey.style,
        StyleVal.getFromString(
            (String) parsedOptionsMap.get("style")));
    options.put(
        NumberFormatterTestOptionKey.unit,
        parsedOptionsMap.get("unit"));
    options.put(
        NumberFormatterTestOptionKey.unitDisplay,
        UnitDisplayVal.getFromString(
            (String) parsedOptionsMap.get("unitDisplay")));
    options.put(
        NumberFormatterTestOptionKey.currency,
        parsedOptionsMap.get("currency"));
    options.put(
        NumberFormatterTestOptionKey.currencyDisplay,
        CurrencyDisplayVal.getFromString(
            (String) parsedOptionsMap.get("currencyDisplay")));
    options.put(
        NumberFormatterTestOptionKey.minimumFractionDigits,
        parsedOptionsMap.getOrDefault("minimumFractionDigits", -1));
    options.put(
        NumberFormatterTestOptionKey.maximumFractionDigits,
        parsedOptionsMap.getOrDefault("maximumFractionDigits", -1));
    options.put(
        NumberFormatterTestOptionKey.minimumIntegerDigits,
        parsedOptionsMap.getOrDefault("minimumIntegerDigits", -1));
    options.put(
        NumberFormatterTestOptionKey.minimumSignificantDigits,
        parsedOptionsMap.getOrDefault("minimumSignificantDigits", -1));
    options.put(
        NumberFormatterTestOptionKey.maximumSignificantDigits,
        parsedOptionsMap.getOrDefault("maximumSignificantDigits", -1));
    options.put(
        NumberFormatterTestOptionKey.nu,
        NuVal.getFromString(
            (String) parsedOptionsMap.get("nu")));
    options.put(
        NumberFormatterTestOptionKey.roundingPriority,
        RoundingPriorityVal.getFromString(
            (String) parsedOptionsMap.get("roundingPriority")));
    options.put(
        NumberFormatterTestOptionKey.roundingMode,
        RoundingModeVal.getFromString(
            (String) parsedOptionsMap.get("roundingMode")));
    int roundingIncrement =
        (int) parsedOptionsMap.getOrDefault("roundingIncrement", RoundingIncrementUtil.DEFAULT);
    assert RoundingIncrementUtil.isValidVal(roundingIncrement);
    options.put(
        NumberFormatterTestOptionKey.roundingIncrement,
        roundingIncrement
    );
    options.put(
        NumberFormatterTestOptionKey.trailingZeroDisplay,
        TrailingZeroDispalyVal.getFromString(
            (String) parsedOptionsMap.get("trailingZeroDisplay")));
    options.put(
        NumberFormatterTestOptionKey.useGrouping,
        UseGroupingVal.getFromString(
            "" + parsedOptionsMap.get("useGrouping")));
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
  public ITestTypeOutputJson getDefaultOutputJson() {
    return new NumberFormatterOutputJson();
  }

  @Override
  public IMap<String, Object> convertOutputToMap(ITestTypeOutputJson outputJson) {
    NumberFormatterOutputJson output = (NumberFormatterOutputJson) outputJson;
    return new io.lacuna.bifurcan.Map<String,Object>()
        .put("label", output.label)
        .put("result", output.result);
  }

  @Override
  public String formatOutputJson(ITestTypeOutputJson outputJson) {
    return ExecutorUtils.GSON.toJson((NumberFormatterOutputJson) outputJson);
  }

  public String getFormattedNumber(NumberFormatterInputJson input) {
    BigDecimal inputVal = new BigDecimal(input.input);

    LocalizedNumberFormatter nf;
    ULocale locale = ULocale.forLanguageTag(input.locale);

    // If there is a skeleton, that's all we need. Apply it and return the result
    if (!input.skeleton.isEmpty()) {
      nf = NumberFormatter.forSkeleton(input.skeleton)
          .locale(locale);
      return nf.format(inputVal).toString();
    }

    // Otherwise (=> no skeleton), set all the options on the formatter

    nf = NumberFormatter.withLocale(locale);
    if (input.options.get("style") == StyleVal.currency && input.options.get("currency") != null) {
      nf = nf.unit(Currency.getInstance((String) input.options.get("currency")));
    }

    FormattedNumber fn = nf.format(inputVal);
    return fn.toString();
  }
}
