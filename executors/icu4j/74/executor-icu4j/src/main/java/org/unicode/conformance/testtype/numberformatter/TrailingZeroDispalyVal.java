package org.unicode.conformance.testtype.numberformatter;

public enum TrailingZeroDispalyVal {
  NONE,  // a fake value to use as default
  auto,
  stringIfInteger;

  public static TrailingZeroDispalyVal DEFAULT = NONE;

  public static TrailingZeroDispalyVal getFromString(String s) {
    try {
      return TrailingZeroDispalyVal.valueOf(s);
    } catch (Exception e) {
      return DEFAULT;
    }
  }
}
