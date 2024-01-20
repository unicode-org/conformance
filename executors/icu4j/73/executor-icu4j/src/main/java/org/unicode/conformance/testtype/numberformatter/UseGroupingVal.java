package org.unicode.conformance.testtype.numberformatter;

/**
 * This enum uses names different from the string literals coming via the JSON
 * because `short`, `long` are reserved keywords in Java.
 * Instead, the uppercase versions `SHORT`, `LONG` are used.
 */
public enum UseGroupingVal {
  FALSE,
  TRUE,
  ALWAYS,
  AUTO,
  MIN2;

  public static UseGroupingVal DEFAULT = AUTO;

  /**
   * Convenience static constructor for this class's enums that automatically
   * uppercases the input string, because the values must be uppercased because
   * some of them conflict with Java keywords in lowercase.
   * @param s
   * @return
   */
  public static UseGroupingVal getFromString(String s) {
    try {
      return UseGroupingVal.valueOf(s.toUpperCase());
    } catch (Exception e) {
      return DEFAULT;
    }
  }

  public String toString() {
    return this.name().toLowerCase();
  }
}
