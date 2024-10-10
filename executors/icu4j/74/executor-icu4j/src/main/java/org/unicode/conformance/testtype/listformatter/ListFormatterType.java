package org.unicode.conformance.testtype.listformatter;

public enum ListFormatterType {
  CONJUNCTION,
  DISJUNCTION,
  UNIT;

  public static org.unicode.conformance.testtype.listformatter.ListFormatterType DEFAULT = CONJUNCTION;

  public static org.unicode.conformance.testtype.listformatter.ListFormatterType getFromString(String s) {
    try {
      return org.unicode.conformance.testtype.listformatter.ListFormatterType.valueOf(s.toUpperCase());
    } catch (Exception e){
      return DEFAULT;
    }
  }
}
