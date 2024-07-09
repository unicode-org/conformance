package org.unicode.conformance.testtype.numberformatter;

public enum SignDisplayVal {
  auto,
  always,
  exceptZero,
  negative,
  never;

  public static SignDisplayVal DEFAULT = auto;

  public static SignDisplayVal getFromString(String s) {
    try {
      return SignDisplayVal.valueOf(s);
    } catch (Exception e){
      return DEFAULT;
    }
  }
}
