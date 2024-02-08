package org.unicode.conformance.testtype.collator;

import org.unicode.conformance.testtype.ITestTypeOutputJson;

public class CollatorOutputJson implements ITestTypeOutputJson {

  public String test_type;

  public String label;

  // Comment this out for now. Only bring back if needed
  // public boolean verify;

  public boolean result;

  public String locale;

  public Integer compare_result;

  public Integer compare;

  public String compare_type;

  public String compare_comment;

  public String test_description;

  public String rules;

  public String s1;

  public String s2;

  public String[] attributes;

  public boolean ignorePunctuation;

  public Integer line;

  public String error;

  public String error_message;

  public String actual_options;
}
