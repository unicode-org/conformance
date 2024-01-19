package org.unicode.conformance.testtype.numberformatter;

/**
 * This enum uses names different from the string literals coming via the JSON
 * because `short`, `long` are reserved keywords in Java.
 * Instead, the uppercase versions `SHORT`, `LONG` are used.
 */
public enum CompactDisplayVal {
  SHORT,
  LONG;

  /**
   * Convenience static constructor for this class's enums that automatically
   * uppercases the input string, because the values must be uppercased because
   * some of them conflict with Java keywords in lowercase.
   * @param s
   * @return
   */
  public static CompactDisplayVal getFromString(String s) {
    return CompactDisplayVal.valueOf(s.toUpperCase());
  }

  public String toString() {
    return this.name().toLowerCase();
  }
}
