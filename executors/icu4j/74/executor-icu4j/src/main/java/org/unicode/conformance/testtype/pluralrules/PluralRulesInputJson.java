package org.unicode.conformance.testtype.pluralrules;

import org.unicode.conformance.testtype.ITestTypeInputJson;

public class PluralRulesInputJson  implements ITestTypeInputJson {
  public String test_type;

  public String label;

  public String locale;

  public PluralRulesType plural_type;

  public double sample;
}
