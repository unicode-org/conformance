package org.unicode.conformance.testtype.relativedatetimeformat;

public enum RelativeDateFormatNumeric {
  ALWAYS,
  AUTO;

  public static org.unicode.conformance.testtype.relativedatetimeformat.RelativeDateFormatNumeric DEFAULT = ALWAYS;

  public static org.unicode.conformance.testtype.relativedatetimeformat.RelativeDateFormatNumeric getFromString(String s) {
    try {
      return org.unicode.conformance.testtype.relativedatetimeformat.RelativeDateFormatNumeric.valueOf(s.toUpperCase());
    } catch (Exception e){
      return DEFAULT;
    }
  }
}
