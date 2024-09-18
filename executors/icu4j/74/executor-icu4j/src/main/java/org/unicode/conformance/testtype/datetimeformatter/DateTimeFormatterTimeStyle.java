package org.unicode.conformance.testtype.datetimeformatter;

public enum DateTimeFormatterTimeStyle {
  FULL,
  LONG,
  MEDIUM,
  SHORT;

  public static org.unicode.conformance.testtype.datetimeformatter.DateTimeFormatterTimeStyle DEFAULT = MEDIUM;

  public static org.unicode.conformance.testtype.datetimeformatter.DateTimeFormatterTimeStyle getFromString(
      String s) {
    try {
      return org.unicode.conformance.testtype.datetimeformatter.DateTimeFormatterTimeStyle.valueOf(
          s.toUpperCase());
    } catch (Exception e) {
      return DEFAULT;
    }
  }

}

