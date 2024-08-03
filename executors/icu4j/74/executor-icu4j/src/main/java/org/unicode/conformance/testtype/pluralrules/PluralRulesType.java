package org.unicode.conformance.testtype.pluralrules;

public enum PluralRulesType {
  CARDINAL,
  ORDINAL;

  public static org.unicode.conformance.testtype.pluralrules.PluralRulesType DEFAULT = CARDINAL;

  public static org.unicode.conformance.testtype.pluralrules.PluralRulesType getFromString(String s) {
    try {
      return org.unicode.conformance.testtype.pluralrules.PluralRulesType.valueOf(s.toUpperCase());
    } catch (Exception e){
      return DEFAULT;
    }
  }
}
