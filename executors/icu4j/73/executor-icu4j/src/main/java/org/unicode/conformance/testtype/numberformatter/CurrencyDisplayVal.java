package org.unicode.conformance.testtype.numberformatter;

public enum CurrencyDisplayVal {
  NONE,  // a fake value to use as default
  symbol,
  narrowSymbol,
  code,
  name;

  public static CurrencyDisplayVal DEFAULT = NONE;

  public static CurrencyDisplayVal getFromString(String s) {
    try {
      return CurrencyDisplayVal.valueOf(s);
    } catch (Exception e) {
      return DEFAULT;
    }
  }
}
