package org.unicode.conformance.testtype.datetimeformatter;

import java.time.Instant;

import java.util.Date;
import com.ibm.icu.util.Calendar;
import com.ibm.icu.util.TimeZone;

import java.util.Locale;

import org.unicode.conformance.testtype.ITestTypeInputJson;

public class DateTimeFormatterInputJson implements ITestTypeInputJson {

  public String testType;

  public String label;

  public String locale_string;
  public Locale locale_with_calendar;

  // UTC formatted instant in time
  public String inputString;

  public Instant time_instant;
  public Date myDate;

  public String skeleton;

  public DateTimeFormatterDateStyle dateStyle;

  public DateTimeFormatterTimeStyle timeStyle;

  // TODO!!!
  public String calendar_string;
  // Set calendar from calendar_string!
  public Calendar calendar;

  public String numberingSystem;

  public TimeZone timeZone;

  public String timeZoneName;
}
