package org.unicode.conformance.testtype.datetimeformatter;

import java.util.Date;

import com.ibm.icu.util.Calendar;
import com.ibm.icu.text.DateFormat;
import com.ibm.icu.util.ULocale;

import io.lacuna.bifurcan.IMap;
import io.lacuna.bifurcan.Map;

import java.util.Collection;

import org.unicode.conformance.ExecutorUtils;
import org.unicode.conformance.testtype.ITestType;
import org.unicode.conformance.testtype.ITestTypeInputJson;
import org.unicode.conformance.testtype.ITestTypeOutputJson;
import org.unicode.conformance.testtype.datetimeformatter.DateTimeFormatterInputJson;
import org.unicode.conformance.testtype.datetimeformatter.DateTimeFormatterInputJson;

public class DateTimeFormatterTester implements ITestType {

  public static DateTimeFormatterTester INSTANCE = new DateTimeFormatterTester();

  @Override
  public ITestTypeInputJson inputMapToJson(Map<String, Object> inputMapData) {
    DateTimeFormatterInputJson result = new DateTimeFormatterInputJson();

    result.label = (String) inputMapData.get("label", null);
    result.locale = (String) inputMapData.get("locale", null);

    result.inputString = (String) inputMapData.get("input_string", null);
    result.myDate = dtf.parse(imput.inputString);

    java.util.Map<String, Object> inputOptions =
        (java.util.Map<String, Object>) inputMapData.get("options", null);

    result.dateStyle = DateTimeFormatterType.getFromString(
        "" + inputOptions.get("dateStyle")
    );

    result.timeStyle = DateTimeFormatterType.getFromString(
        "" + inputOptions.get("timeStyle")
    );

    result.calendarString = DateTimeFormatterType.getFromString(
        "" + inputOptions.get("calendar")
    );

    // TODO!!! Get calendar object. Depends on timezone and locale.
    result.numberingSystem = DateTimeFormatterType.getFromString(
        "" + inputOptions.get("numberingSystem")
    );

    result.timeZone = DateTimeFormatterType.getFromString(
        "" + inputOptions.get("timeZone")
    );

    result.timeZoneName = DateTimeFormatterType.getFromString(
        "" + inputOptions.get("timeZoneName")
    );

    return result;
  }

  public ITestTypeOutputJson execute(ITestTypeInputJson inputJson) {
    DateTimeFormatterInputJson input = (DateTimeFormatterInputJson) inputJson;

    // partially construct output
    DateTimeFormatterOutputJson output = (DateTimeFormatterOutputJson) getDefaultOutputJson();
    output.label = input.label;

    try {
      output.result = getDateTimeFormatResultString(input);
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
    return new DateTimeFormatterOutputJson();
  }

  public IMap<String, Object> convertOutputToMap(ITestTypeOutputJson outputJson) {
    DateTimeFormatterOutputJson output = (DateTimeFormatterOutputJson) outputJson;
    return new io.lacuna.bifurcan.Map<String, Object>()
        .put("label", output.label)
        .put("result", output.result);
  }

  @Override
  public String formatOutputJson(ITestTypeOutputJson outputJson) {
    return ExecutorUtils.GSON.toJson((DateTimeFormatterOutputJson) outputJson);
  }

  public String getDateTimeFormatterResultString(DateTimeFormatterInputJson input) {

    ULocale locale = ULocale.forLanguageTag(input.locale);

    int dateStyle;
    int timeStyle;
    switch (input.dateStyle) {
      case DateTimeFormattertyle.dateStyle.FULL:
        dateStyle = DateFormat.FULL;
        break;
      case DateTimeFormattertyle.dateStyle.LONG:
        dateStyle = DateFormat.LONG;
        break;
      default:
      case DateTimeFormattertyle.dateStyle.MEDIUM:
        dateStyle = DateFormat.MEDIUM;
        break;
      case DateTimeFormattertyle.dateStyle.SHORT:
        dateStyle = DateFormat.SHORT;
        break;
      case DateTimeFormattertyle.dateStyle.NARROW:
        dateStyle = DateFormat.NARROW;
        break;
    }

    int timeStyle;
    switch (input.timeStyle) {
      case DateTimeFormattertyle.timeStyle.FULL:
        timeStyle = DateFormat.FULL;
        break;
      case DateTimeFormattertyle.timeStyle.LONG:
        timeStyle = DateFormat.LONG;
        break;
      default:
      case DateTimeFormattertyle.timeStyle.MEDIUM:
        timeStyle = DateFormat.MEDIUM;
        break;
      case DateTimeFormattertyle.timeStyle.SHORT:
        timeStyle = DateFormat.SHORT;
        break;
      case DateTimeFormattertyle.timeStyle.NARROW:
        timeStyle = DateFormat.NARROW;
        break;
    }

    // Get calendar and timezone as needed.
    Calendar cal = input.calendar;

    DateFormat dtf = DateFormat.getDateTimeInstance(cal, dateStyle, timeStyle, locale);

    return dtf.format(input.myDate);
  }

}