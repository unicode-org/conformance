package org.unicode.conformance.testtype.relativedatetimeformat;

import com.ibm.icu.text.DisplayContext;
import com.ibm.icu.text.NumberFormat;
import com.ibm.icu.text.RelativeDateTimeFormatter;
import com.ibm.icu.text.RelativeDateTimeFormatter.Style;
import com.ibm.icu.util.ULocale;

import io.lacuna.bifurcan.IMap;
import io.lacuna.bifurcan.Map;

import org.unicode.conformance.ExecutorUtils;
import org.unicode.conformance.testtype.ITestType;
import org.unicode.conformance.testtype.ITestTypeInputJson;
import org.unicode.conformance.testtype.ITestTypeOutputJson;

public class RelativeDateTimeFormatTester implements ITestType {

  public static RelativeDateTimeFormatTester INSTANCE = new RelativeDateTimeFormatTester();

  @Override
  public ITestTypeInputJson inputMapToJson(Map<String, Object> inputMapData) {
    RelativeDateTimeFormatInputJson result = new RelativeDateTimeFormatInputJson();

    result.label = (String) inputMapData.get("label", null);
    result.locale = (String) inputMapData.get("locale", null);
    result.count = (String) inputMapData.get("count", "0");
    result.quantity = Double.parseDouble(result.count);
    result.numberingSystem = "";

    java.util.Map<String, Object> inputOptions =
        (java.util.Map<String, Object>) inputMapData.get("options", null);
    if (inputOptions != null) {
      result.numberingSystem = (String) inputOptions.get("numberingSystem");
      if (result.numberingSystem != "") {
        result.locale = result.locale + "-u-nu-" + result.numberingSystem;
      }
    }

    if (inputOptions != null) {
      result.style = RelativeDateTimeFormatStyle.getFromString(
          "" + inputOptions.get("style"));

      result.numeric = RelativeDateFormatNumeric.getFromString(
          "" + inputOptions.get("numeric"));
    }

    String unitInput = (String) inputMapData.get("unit", "0");
    result.unit = RelativeDateTimeFormatUnits.getFromString(
        unitInput);

    return result;
  }

  @Override
  public ITestTypeOutputJson execute(ITestTypeInputJson inputJson) {
    RelativeDateTimeFormatInputJson input = (RelativeDateTimeFormatInputJson) inputJson;

    // partially construct output
    RelativeDateTimeFormatOutputJson output = (RelativeDateTimeFormatOutputJson) getDefaultOutputJson();
    output.label = input.label;

    try {
      output.result = getRelativeDateTimeFormatResultString(input);
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
    return new RelativeDateTimeFormatOutputJson();
  }

  public IMap<String, Object> convertOutputToMap(ITestTypeOutputJson outputJson) {
    RelativeDateTimeFormatOutputJson output = (RelativeDateTimeFormatOutputJson) outputJson;
    return new io.lacuna.bifurcan.Map<String, Object>()
        .put("label", output.label)
        .put("result", output.result);
  }

  public String formatOutputJson(ITestTypeOutputJson outputJson) {
    return ExecutorUtils.GSON.toJson(outputJson);
  }

  public String getRelativeDateTimeFormatResultString(RelativeDateTimeFormatInputJson input) {
    ULocale locale = ULocale.forLanguageTag(input.locale);
    Style style;
    RelativeDateTimeFormatter.RelativeDateTimeUnit unit;

    switch (input.unit) {
      default:
      case DAY:
        unit = RelativeDateTimeFormatter.RelativeDateTimeUnit.DAY;
        break;
      case HOUR:
        unit = RelativeDateTimeFormatter.RelativeDateTimeUnit.HOUR;
        break;
      case MINUTE:
        unit = RelativeDateTimeFormatter.RelativeDateTimeUnit.MINUTE;
        break;
      case MONTH:
        unit = RelativeDateTimeFormatter.RelativeDateTimeUnit.MONTH;
        break;
      case QUARTER:
        unit = RelativeDateTimeFormatter.RelativeDateTimeUnit.QUARTER;
        break;
      case SECOND:
        unit = RelativeDateTimeFormatter.RelativeDateTimeUnit.SECOND;
        break;
      case WEEK:
        unit = RelativeDateTimeFormatter.RelativeDateTimeUnit.WEEK;
        break;
      case YEAR:
        unit = RelativeDateTimeFormatter.RelativeDateTimeUnit.YEAR;
        break;
    }

    switch (input.style) {
      case NARROW:
        style = RelativeDateTimeFormatter.Style.NARROW;
        break;
      case SHORT:
        style = RelativeDateTimeFormatter.Style.SHORT;
        break;
      default:
      case LONG:
        style = RelativeDateTimeFormatter.Style.LONG;
        break;
    }

    NumberFormat nf = null;
    DisplayContext dc = DisplayContext.CAPITALIZATION_NONE;

    RelativeDateTimeFormatter rdtf =
        RelativeDateTimeFormatter.getInstance(locale, nf, style, dc);

    String result;
    if (input.numeric == RelativeDateFormatNumeric.ALWAYS) {
      result = rdtf.formatNumeric(input.quantity, unit);
    } else {
      result = rdtf.format(input.quantity, unit);
    }
    return result;
  }
}
