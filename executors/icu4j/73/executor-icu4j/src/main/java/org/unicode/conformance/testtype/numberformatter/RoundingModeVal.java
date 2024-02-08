package org.unicode.conformance.testtype.numberformatter;

public enum RoundingModeVal {
  NONE,  // a fake value to use as default
  ceil,
  floor,
  expand,
  trunc,
  halfCeil,
  halfFloor,
  halfExpand,
  halfTrunc,
  halfEven,
  unnecessary;

  public static RoundingModeVal DEFAULT = NONE;

  public static RoundingModeVal getFromString(String s) {
    try {
      return RoundingModeVal.valueOf(s);
    } catch (Exception e) {
      return DEFAULT;
    }
  }
}
