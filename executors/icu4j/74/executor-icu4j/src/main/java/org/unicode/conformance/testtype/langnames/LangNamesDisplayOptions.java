package org.unicode.conformance.testtype.langnames;

public enum LangNamesDisplayOptions {
  STANDARD,
  DIALECT;  // DIALECT_NAMES is the ICU4J enum

  public static org.unicode.conformance.testtype.langnames.LangNamesDisplayOptions DEFAULT = STANDARD;

  public static org.unicode.conformance.testtype.langnames.LangNamesDisplayOptions getFromString(String s) {
    try {
      return org.unicode.conformance.testtype.langnames.LangNamesDisplayOptions.valueOf(s.toUpperCase());
    } catch (Exception e){
      return DEFAULT;
    }
  }
}
