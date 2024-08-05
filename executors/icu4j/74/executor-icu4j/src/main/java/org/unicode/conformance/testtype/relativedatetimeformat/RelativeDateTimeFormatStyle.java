package org.unicode.conformance.testtype.relativedatetimeformat;

public enum RelativeDateTimeFormatStyle {
  LONG,
  NARROW,
  SHORT;

  public static org.unicode.conformance.testtype.relativedatetimeformat.RelativeDateTimeFormatStyle DEFAULT = LONG;

  public static org.unicode.conformance.testtype.relativedatetimeformat.RelativeDateTimeFormatStyle getFromString(String s) {
    try {
      return org.unicode.conformance.testtype.relativedatetimeformat.RelativeDateTimeFormatStyle.valueOf(s.toUpperCase());
    } catch (Exception e){
      return DEFAULT;
    }
  }
}
