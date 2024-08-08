package org.unicode.conformance.testtype.datetimeformatter;

import java.text.ParseException;
import java.time.LocalDateTime;
import java.time.ZoneId;
import java.time.format.DateTimeFormatter;

import java.util.Date;

import com.ibm.icu.util.Calendar;
import com.ibm.icu.text.DateFormat;
import com.ibm.icu.util.ULocale;

import io.lacuna.bifurcan.IMap;
import io.lacuna.bifurcan.Map;


import org.unicode.conformance.ExecutorUtils;
import org.unicode.conformance.testtype.ITestType;
import org.unicode.conformance.testtype.ITestTypeInputJson;
import org.unicode.conformance.testtype.ITestTypeOutputJson;

public class DateTimeFormatterTester implements ITestType {

  public static DateTimeFormatterTester INSTANCE = new DateTimeFormatterTester();

  @Override
  public ITestTypeInputJson inputMapToJson(Map<String, Object> inputMapData) {
    DateTimeFormatterInputJson result = new DateTimeFormatterInputJson();

    result.label = (String) inputMapData.get("label", null);
    result.locale = (String) inputMapData.get("locale", null);
    result.skeleton = (String) inputMapData.get("skeleton", null);

    result.inputString = (String) inputMapData.get("input_string", null);

    java.util.Map<String, Object> inputOptions =
        (java.util.Map<String, Object>) inputMapData.get("options", null);

    result.timeZone = (String) inputOptions.get("timeZone");
    ZoneId thisZoneId;
    if (result.timeZone == null) {
      thisZoneId = ZoneId.systemDefault();
    } else {
      thisZoneId = ZoneId.of(result.timeZone);
    }

    // Extract ISO part of the input string to parse.
    String inputStringDateTime = result.inputString.substring(0, 25);

    // For parsing the input string and converting to java.util.date
    LocalDateTime parsedLocalDateTime =
        LocalDateTime.parse(inputStringDateTime, DateTimeFormatter.ISO_OFFSET_DATE_TIME);
    result.myDate =
        java.util.Date.from(parsedLocalDateTime.atZone(thisZoneId)
            .toInstant());

    result.dateStyle = DateTimeFormatterDateStyle.getFromString(
        "" + inputOptions.get("dateStyle")
    );

    result.timeStyle = DateTimeFormatterTimeStyle.getFromString(
        "" + inputOptions.get("timeStyle")
    );

    result.calendarString = (String) inputOptions.get("calendar");

    // TODO!!! Get calendar object. Depends on timezone and locale.
    // Just a placeholder for now.
    result.calendar = Calendar.getInstance();

    result.numberingSystem = (String) inputOptions.get("numberingSystem");

    result.timeZoneName = (String) inputOptions.get("timeZoneName");

    return result;
  }

  public ITestTypeOutputJson execute(ITestTypeInputJson inputJson) {
    DateTimeFormatterInputJson input = (DateTimeFormatterInputJson) inputJson;

    // partially construct output
    DateTimeFormatterOutputJson output = (DateTimeFormatterOutputJson) getDefaultOutputJson();
    output.label = input.label;

    try {
      output.result = getDateTimeFormatterResultString(input);
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
    switch (input.dateStyle) {
      case FULL:
        dateStyle = DateFormat.FULL;
        break;
      case LONG:
        dateStyle = DateFormat.LONG;
        break;
      default:
      case MEDIUM:
        dateStyle = DateFormat.MEDIUM;
        break;
      case SHORT:
        dateStyle = DateFormat.SHORT;
        break;
    }

    int timeStyle;
    switch (input.timeStyle) {
      case FULL:
        timeStyle = DateFormat.FULL;
        break;
      case LONG:
        timeStyle = DateFormat.LONG;
        break;
      default:
      case MEDIUM:
        timeStyle = DateFormat.MEDIUM;
        break;
      case SHORT:
        timeStyle = DateFormat.SHORT;
        break;

    }

    // Get calendar and timezone as needed.
    Calendar cal = input.calendar;

    DateFormat dtf;
    if (input.skeleton != null) {
      dtf = DateFormat.getInstanceForSkeleton(cal, input.skeleton, locale);
    } else {
      dtf = DateFormat.getDateTimeInstance(cal, dateStyle, timeStyle, locale);
    }

    return dtf.format(input.myDate);
  }

}