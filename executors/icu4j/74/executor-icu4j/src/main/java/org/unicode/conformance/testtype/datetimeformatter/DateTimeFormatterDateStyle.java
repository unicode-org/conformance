package org.unicode.conformance.testtype.datetimeformatter;

public enum DateTimeFormatterDateStyle {
  FULL,
  LONG,
  MEDIUM,
  SHORT,
  NARROW;

  public static org.unicode.conformance.testtype.datetimeformatter.DateTimeFormatterDateStyle DEFAULT = MEDIUM;

  public static org.unicode.conformance.testtype.datetimeformatter.DateTimeFormatterDateStyle getFromString(
      String s) {
    try {
      return org.unicode.conformance.testtype.datetimeformatter.DateTimeFormatterDateStyle.valueOf(
          s.toUpperCase());
    } catch (Exception e) {
      return DEFAULT;
    }
  }

}
