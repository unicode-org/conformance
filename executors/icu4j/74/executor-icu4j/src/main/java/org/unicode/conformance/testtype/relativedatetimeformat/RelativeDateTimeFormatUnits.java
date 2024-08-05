package org.unicode.conformance.testtype.relativedatetimeformat;

public enum RelativeDateTimeFormatUnits {
  DAY,
  HOUR,
  MINUTE,
  MONTH,
  QUARTER,
  SECOND,
  WEEK,
  YEAR;

  public static org.unicode.conformance.testtype.relativedatetimeformat.RelativeDateTimeFormatUnits DEFAULT = DAY;

  public static org.unicode.conformance.testtype.relativedatetimeformat.RelativeDateTimeFormatUnits getFromString(String s) {
    try {
      return org.unicode.conformance.testtype.relativedatetimeformat.RelativeDateTimeFormatUnits.valueOf(s.toUpperCase());
    } catch (Exception e){
      return DEFAULT;
    }
  }
}
