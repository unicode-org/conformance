package org.unicode.conformance.testtype.numberformatter;

public enum RoundingPriorityVal {
  NONE,
  auto,
  morePrecision,
  lessPrecision;

  public static RoundingPriorityVal DEFAULT = NONE;

  public static RoundingPriorityVal getFromString(String s) {
    try {
      return RoundingPriorityVal.valueOf(s);
    } catch (Exception e) {
      return DEFAULT;
    }
  }
}
