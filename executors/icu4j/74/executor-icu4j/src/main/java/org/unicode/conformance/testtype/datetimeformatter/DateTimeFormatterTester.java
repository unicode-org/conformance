package org.unicode.conformance.testtype.datetimeformatter;

import java.util.Date;
import java.time.Instant;

import java.util.Locale;
import java.util.Locale.Builder;

import com.ibm.icu.util.Calendar;
import com.ibm.icu.text.DateFormat;
import com.ibm.icu.util.TimeZone;
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
    result.locale_string = (String) inputMapData.get("locale", null);
    result.skeleton = (String) inputMapData.get("skeleton", null);

    // The instant in UTC time.
    result.inputString = (String) inputMapData.get("input_string", null);

    java.util.Map<String, Object> inputOptions =
        (java.util.Map<String, Object>) inputMapData.get("options", null);

    result.timeZoneName = (String) inputOptions.get("timeZone");
    if (result.timeZoneName == null) {
      TimeZone.setDefault(TimeZone.GMT_ZONE);
      result.timeZone = TimeZone.getDefault();
    } else {
      result.timeZone = TimeZone.getTimeZone(result.timeZoneName);
    }

    // Extract ISO part of the input string to parse.
    result.time_instant = Instant.parse(result.inputString);
    result.myDate = Date.from(result.time_instant);

    // For parsing the input string and converting to java.util.date
    result.dateStyle = DateTimeFormatterDateStyle.getFromString(
        "" + inputOptions.get("dateStyle")
    );

    result.timeStyle = DateTimeFormatterTimeStyle.getFromString(
        "" + inputOptions.get("timeStyle")
    );

    result.calendar_string = (String) inputOptions.get("calendar");

    result.locale_with_calendar = new Builder().setLanguageTag(result.locale_string)
        .setUnicodeLocaleKeyword("ca", result.calendar_string)
        .build();

    result.calendar = Calendar.getInstance(result.locale_with_calendar);

    result.numberingSystem = (String) inputOptions.get("numberingSystem");

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

    ULocale locale = ULocale.forLanguageTag(input.locale_string);

    int dateStyle = -1;
    switch (input.dateStyle) {
      case FULL:
        dateStyle = DateFormat.FULL;
        break;
      case LONG:
        dateStyle = DateFormat.LONG;
        break;
      case MEDIUM:
        dateStyle = DateFormat.MEDIUM;
        break;
      case SHORT:
        dateStyle = DateFormat.SHORT;
        break;
      default:
        dateStyle = -1;  // Undefined
        break;
    }

    int timeStyle = -1;
    switch (input.timeStyle) {
      case FULL:
        timeStyle = DateFormat.FULL;
        break;
      case LONG:
        timeStyle = DateFormat.LONG;
        break;
      case MEDIUM:
        timeStyle = DateFormat.MEDIUM;
        break;
      case SHORT:
        timeStyle = DateFormat.SHORT;
        break;
      default:
        timeStyle = -1;  // Undefined
        break;

    }

    // Get calendar and timezone as needed.
    Calendar cal = input.calendar;

    DateFormat dtf;
    if (input.skeleton != null) {
      dtf = DateFormat.getInstanceForSkeleton(cal, input.skeleton, input.locale_with_calendar);
    } else {
      if (dateStyle >=0 && timeStyle >= 0) {
        dtf = DateFormat.getDateTimeInstance(cal, dateStyle, timeStyle, input.locale_with_calendar);
      } else
        if (dateStyle >= 0) {
          dtf = DateFormat.getDateInstance(cal, dateStyle,input.locale_with_calendar);
        } else
          if (timeStyle >= 0) {
            dtf = DateFormat.getTimeInstance(cal, timeStyle, input.locale_with_calendar);
          } else {
            dtf = DateFormat.getInstance(cal, input.locale_with_calendar);
          }
    }
    dtf.setCalendar(input.calendar);
    dtf.setTimeZone(input.timeZone);

    return dtf.format(input.myDate);
  }

}