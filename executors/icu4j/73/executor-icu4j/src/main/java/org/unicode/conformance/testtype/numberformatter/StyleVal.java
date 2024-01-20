package org.unicode.conformance.testtype.numberformatter;

public enum StyleVal {
  NONE, // a fake value to use as default
  decimal,
  currency,
  percent,
  unit;

  public static StyleVal DEFAULT = NONE;

  public static StyleVal getFromString(String s) {
    try {
      return StyleVal.valueOf(s);
    } catch (Exception e) {
      return DEFAULT;
    }
  }
}
