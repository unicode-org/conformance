package org.unicode.conformance.testtype.listformatter;

public enum ListFormatterWidth {
  NARROW,
  SHORT,
  LONG;

  public static org.unicode.conformance.testtype.listformatter.ListFormatterWidth DEFAULT = LONG;

  public static org.unicode.conformance.testtype.listformatter.ListFormatterWidth getFromString(String s) {
    try {
      return org.unicode.conformance.testtype.listformatter.ListFormatterWidth.valueOf(s.toUpperCase());
    } catch (Exception e){
      return DEFAULT;
    }
  }
}
