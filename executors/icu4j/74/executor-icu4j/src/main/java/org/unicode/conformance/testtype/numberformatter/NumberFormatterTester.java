package org.unicode.conformance.testtype.numberformatter;

import com.ibm.icu.number.FormattedNumber;
import com.ibm.icu.number.FractionPrecision;
import com.ibm.icu.number.IntegerWidth;
import com.ibm.icu.number.LocalizedNumberFormatter;
import com.ibm.icu.number.Notation;
import com.ibm.icu.number.NumberFormatter;
import com.ibm.icu.number.NumberFormatter.GroupingStrategy;
import com.ibm.icu.number.NumberFormatter.RoundingPriority;
import com.ibm.icu.number.NumberFormatter.SignDisplay;
import com.ibm.icu.number.NumberFormatter.TrailingZeroDisplay;
import com.ibm.icu.number.NumberFormatter.UnitWidth;
import com.ibm.icu.number.Precision;
import com.ibm.icu.text.NumberingSystem;
import com.ibm.icu.util.Currency;
import com.ibm.icu.util.MeasureUnit;
import com.ibm.icu.util.NoUnit;
import com.ibm.icu.util.ULocale;
import io.lacuna.bifurcan.IMap;
import io.lacuna.bifurcan.Map;
import java.math.BigDecimal;
import java.math.RoundingMode;
import java.util.HashMap;
import java.util.regex.Pattern;
import java.util.regex.Matcher;
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

    // Check for unsupported patterns
    if (input.pattern != null && input.pattern != "") {
      Pattern check1 = Pattern.compile("0+0.#+E");
      Matcher matcher1 = check1.matcher(input.pattern);
      Pattern check2 = Pattern.compile("^.0#*E");
      Matcher matcher2 = check2.matcher(input.pattern);
      if (matcher1.find() || matcher2.find()) {
        output.error_type = "unsupported";
        output.unsupported = "unsupported pattern";
        output.error_detail = input.pattern;
        return output;
      }
    }

    // Check unsupport options in skeleton
    if (input.skeleton != null) {
      Pattern check_unnessary = Pattern.compile("rounding-mode-(unnecessary|half-odd)");
      Matcher matcher1 = check_unnessary.matcher(input.skeleton);
      if (matcher1.find()) {
        output.error_type = "unsupported";
        output.unsupported = "skeleton option";
        output.error_detail = matcher1.group();
        return output;
      }

    }
    try {
      output.result = getFormattedNumber(input);
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

    ULocale locale = ULocale.ROOT;
    if (input.locale != null) {
      locale = ULocale.forLanguageTag(input.locale);
    }

    // Return early with a result f there is a skeleton, since that's all we need for configs.
    if (input.skeleton != null && !input.skeleton.isEmpty()) {
      nf = NumberFormatter.forSkeleton(input.skeleton)
          .locale(locale);
      return nf.format(inputVal).toString();
    }

    // Otherwise (=> no skeleton), set all the options on the formatter

    nf = NumberFormatter.withLocale(locale);

    String styleStr = null;
    if (input.options.containsKey(NumberFormatterTestOptionKey.style)) {
      styleStr = ((StyleVal) input.options.get(NumberFormatterTestOptionKey.style)).name();
    }
    StyleVal style = StyleVal.getFromString(styleStr);

    if (style == StyleVal.currency) {
      String currency = (String) input.options.get(NumberFormatterTestOptionKey.currency);
      nf = nf.unit(Currency.getInstance(currency));

      // TODO: determine if & how to utilize currency display options ("currency symbol name styles")
      // CurrencyDisplayVal currencyDisplay =
      //     (CurrencyDisplayVal) input.options.get(NumberFormatterTestOptionKey.currencyDisplay);
    } else if (style == StyleVal.unit) {
      String unitStr = (String) input.options.get(NumberFormatterTestOptionKey.unit);
      MeasureUnit unit = MeasureUnit.forIdentifier(unitStr);
      nf = nf.unit(unit);

      UnitDisplayVal unitDisplay =
          (UnitDisplayVal) input.options.get(NumberFormatterTestOptionKey.unitDisplay);
      switch (unitDisplay) {
        case NONE:
          break;
        case LONG:
          nf = nf.unitWidth(UnitWidth.FULL_NAME);
          break;
        case SHORT:
          nf = nf.unitWidth(UnitWidth.SHORT);
          break;
        case NARROW:
          nf = nf.unitWidth(UnitWidth.NARROW);
          break;
      }
    } else if (style == StyleVal.percent) {
      nf = nf.unit(NoUnit.PERCENT);
    } else {
      assert style == StyleVal.decimal || style == StyleVal.NONE;
    }

    if (input.options.containsKey(NumberFormatterTestOptionKey.notation)) {
      String notationStr = (String) input.options.get(NumberFormatterTestOptionKey.notation);
      if (notationStr != null) {
        switch (notationStr) {
          case "compact":
            CompactDisplayVal compactDisplay = (CompactDisplayVal) input.options.get(
                NumberFormatterTestOptionKey.compactDisplay);
            switch (compactDisplay) {
              case LONG:
                nf = nf.notation(Notation.compactLong());
                break;
              case SHORT:
                nf = nf.notation(Notation.compactShort());
                break;
            }
            break;
          case "engineering":
            nf = nf.notation(Notation.engineering());
            break;
          case "scientific":
            nf = nf.notation(Notation.scientific());
            break;
          case "simple":
            nf = nf.notation(Notation.simple());
            break;
        }
      }
    }
    if (input.options.containsKey(NumberFormatterTestOptionKey.signDisplay)) {
      SignDisplayVal signDisplay =
          (SignDisplayVal) input.options.get(NumberFormatterTestOptionKey.signDisplay);
      switch (signDisplay) {
        case auto:
          nf = nf.sign(SignDisplay.AUTO);
          break;
        case never:
          nf = nf.sign(SignDisplay.NEVER);
          break;
        case always:
          nf = nf.sign(SignDisplay.ALWAYS);
          break;
        case exceptZero:
          nf = nf.sign(SignDisplay.EXCEPT_ZERO);
          break;
        case negative:
          nf = nf.sign(SignDisplay.NEGATIVE);
          break;
      }
    }
    if (input.options.containsKey(NumberFormatterTestOptionKey.minimumIntegerDigits)) {
      IntegerWidth width = IntegerWidth.zeroFillTo(0);
      if (input.options.containsKey(NumberFormatterTestOptionKey.minimumIntegerDigits)) {
        Number minIntDigits =
            (Number) input.options.get(NumberFormatterTestOptionKey.minimumIntegerDigits);
        width = IntegerWidth.zeroFillTo(minIntDigits.intValue());
      }
      nf = nf.integerWidth(width);
    }
    if (input.options.containsKey(NumberFormatterTestOptionKey.minimumFractionDigits)
        || input.options.containsKey(NumberFormatterTestOptionKey.maximumFractionDigits)) {
      // parse fraction digits (min / max)
      Precision precision = null;
      FractionPrecision fractionPrecision = null;
      Number minDigits = null;
      Number maxDigits = null;
      if (input.options.containsKey(NumberFormatterTestOptionKey.minimumFractionDigits)) {
        minDigits =
            (Number) input.options.get(NumberFormatterTestOptionKey.minimumFractionDigits);
      }
      if (input.options.containsKey(NumberFormatterTestOptionKey.maximumFractionDigits)) {
        maxDigits =
            (Number) input.options.get(NumberFormatterTestOptionKey.maximumFractionDigits);
      }

      // handle fraction digits
      if (minDigits != null && maxDigits != null) {
        fractionPrecision = Precision.minMaxFraction(minDigits.intValue(), maxDigits.intValue());
      } else if (minDigits != null) {
        fractionPrecision = Precision.minFraction(minDigits.intValue());
      } else if (maxDigits != null) {
        fractionPrecision = Precision.maxFraction(maxDigits.intValue());
      }

      // parse significant digits (min / max / rounding priority)
      Number sigFigMinDigits = null;
      Number sigFigMaxDigits = null;
      RoundingPriority priority = null;
      if (fractionPrecision != null
          && input.options.containsKey(NumberFormatterTestOptionKey.minimumSignificantDigits)
          && input.options.containsKey(NumberFormatterTestOptionKey.maximumSignificantDigits)
          && input.options.containsKey(NumberFormatterTestOptionKey.roundingPriority)) {

        if (input.options.containsKey(NumberFormatterTestOptionKey.minimumSignificantDigits)) {
          sigFigMinDigits =
              (Number) input.options.get(NumberFormatterTestOptionKey.minimumSignificantDigits);
        }
        if (input.options.containsKey(NumberFormatterTestOptionKey.maximumSignificantDigits)) {
          sigFigMaxDigits =
              (Number) input.options.get(NumberFormatterTestOptionKey.maximumSignificantDigits);
        }
        RoundingPriorityVal roundingPriorityVal =
            (RoundingPriorityVal) input.options.get(
                NumberFormatterTestOptionKey.roundingPriority);
        switch (roundingPriorityVal) {
          case NONE:
            // This assumes that `auto` is the default value
          case auto:
            // TODO: how to handle?
            break;
          case morePrecision:
            priority = RoundingPriority.STRICT;
            break;
          case lessPrecision:
            priority = RoundingPriority.RELAXED;
            break;
        }
      }

      // handle significant digits
      if (fractionPrecision != null && sigFigMinDigits != null && sigFigMaxDigits != null
          && priority != null) {
        precision = fractionPrecision.withSignificantDigits(
            minDigits.intValue(), maxDigits.intValue(), priority
        );
      } else {
        precision = fractionPrecision;
      }

      if (precision != null
          && input.options.containsKey(NumberFormatterTestOptionKey.trailingZeroDisplay)) {
        TrailingZeroDispalyVal trailingZeroDisplayVal =
            (TrailingZeroDispalyVal) input.options.get(
                NumberFormatterTestOptionKey.trailingZeroDisplay);
        TrailingZeroDisplay trailingZeroDisplay = null;
        switch (trailingZeroDisplayVal) {
          case auto:
          case NONE:
          default:
            trailingZeroDisplay = TrailingZeroDisplay.AUTO;
            break;
          case stringIfInteger:
            trailingZeroDisplay = TrailingZeroDisplay.HIDE_IF_WHOLE;
            break;
        }

        precision.trailingZeroDisplay(trailingZeroDisplay);
      }

      if (precision != null) {
        nf = nf.precision(precision);
      }
    }
    if (input.options.containsKey(NumberFormatterTestOptionKey.nu)) {
      NuVal nu = (NuVal) input.options.get(NumberFormatterTestOptionKey.nu);
      NumberingSystem numberingSystem = NumberingSystem.getInstanceByName(nu.name());
      nf = nf.symbols(numberingSystem);
    }
    if (input.options.containsKey(NumberFormatterTestOptionKey.roundingMode)) {
      RoundingModeVal roundingModeVal =
          (RoundingModeVal) input.options.get(NumberFormatterTestOptionKey.roundingMode);
      RoundingMode roundingMode = null;
      switch (roundingModeVal) {
        case ceil:
          roundingMode = RoundingMode.CEILING;
          break;
        case floor:
          roundingMode = RoundingMode.FLOOR;
          break;
        case expand:
          roundingMode = RoundingMode.UP;
          break;
        case trunc:
          roundingMode = RoundingMode.DOWN;
          break;
        case halfCeil:
          // TODO: support?
          break;
        case halfFloor:
          // TODO: support?
          break;
        case halfExpand:
          roundingMode = RoundingMode.HALF_UP;
          break;
        case halfTrunc:
          roundingMode = RoundingMode.HALF_DOWN;
          break;
        case halfEven:
          roundingMode = RoundingMode.HALF_EVEN;
        case NONE: // default = halfEven
        default:
          break;
        case unnecessary:
          break;
      }
      if (roundingMode != null) {
        nf = nf.roundingMode(roundingMode);
      }
    }
    if (input.options.containsKey(NumberFormatterTestOptionKey.useGrouping)) {
      UseGroupingVal groupingVal =
          (UseGroupingVal) input.options.get(NumberFormatterTestOptionKey.useGrouping);
      GroupingStrategy groupingStrategy = null;
      switch (groupingVal) {
        case FALSE:
          groupingStrategy = GroupingStrategy.OFF;
          break;
        case ALWAYS:
          groupingStrategy = GroupingStrategy.ON_ALIGNED;
          break;
        case AUTO:
        case TRUE:
          groupingStrategy = GroupingStrategy.AUTO;
          break;
        case MIN2:
          groupingStrategy = GroupingStrategy.MIN2;
          break;
      }
      nf = nf.grouping(groupingStrategy);
    }

    FormattedNumber fn = nf.format(inputVal);
    return fn.toString();
  }
}
