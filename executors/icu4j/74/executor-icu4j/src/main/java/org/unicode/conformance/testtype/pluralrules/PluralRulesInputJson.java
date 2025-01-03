package org.unicode.conformance.testtype.pluralrules;

import org.unicode.conformance.testtype.ITestTypeInputJson;

public class PluralRulesInputJson  implements ITestTypeInputJson {
  public String test_type;

  public String label;

  public String locale;

  public PluralRulesType pluralType;

  public String sampleString;

  public double sample;
}
