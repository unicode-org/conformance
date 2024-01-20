package org.unicode.conformance.testtype.numberformatter;

/**
 * This enum uses names different from the string literals coming via the JSON
 * because `short`, `long` are reserved keywords in Java.
 * Instead, the uppercase versions `SHORT`, `LONG`, etc. are used.
 */
public enum UnitDisplayVal {
  NONE, // a fake value to use as default
  LONG,
  SHORT,
  NARROW;

  public static UnitDisplayVal DEFAULT = NONE;

  /**
   * Convenience static constructor for this class's enums that automatically
   * uppercases the input string, because the values must be uppercased because
   * some of them conflict with Java keywords in lowercase.
   * @param s
   * @return
   */
  public static UnitDisplayVal getFromString(String s) {
    try {
      return UnitDisplayVal.valueOf(s.toUpperCase());
    } catch (Exception e) {
      return DEFAULT;
    }
  }

  public String toString() {
    return this.name().toLowerCase();
  }
}
