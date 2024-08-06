package org.unicode.conformance.testtype.datetimeformatter;

import java.util.Date;
import com.ibm.icu.util.Calendar;

import org.unicode.conformance.testtype.ITestTypeInputJson;

public class DateTimeFormatterInputJson implements ITestTypeInputJson {

  public String testType;

  public String label;

  // UTC formatted time
  public String inputString;

  public Date myDate;

  public String skeleton;

  public DateTimeFormatterDateStyle dateStyle;

  public DateTimeFormatterTimeStyle timeStyle;

  // TODO!!!
  public String calendarString;
  // Set calendar from calendarString!
  public Calendar calendar;

  public String numberingSystem;

  public String timeZone;

  public String timeZoneName;

}
