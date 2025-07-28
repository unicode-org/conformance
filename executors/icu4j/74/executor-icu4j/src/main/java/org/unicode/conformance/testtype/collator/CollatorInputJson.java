package org.unicode.conformance.testtype.collator;

import java.util.ArrayList;
import org.unicode.conformance.testtype.ITestTypeInputJson;

public class CollatorInputJson implements ITestTypeInputJson {

  public String test_type;

  public String label;

  public String s1;

  public String s2;

  public String locale;

  public boolean ignorePunctuation;

  public Integer line;

  public String strength;

 public String compare_type;

  public String test_description;

  public ArrayList<String> attributes;

  public String rules;

  public String reorder_string;
  public int[] reorder_codes;

 public String reorder;

 public String case_first;

 public String backwards;

 public String compare_comment;

  public String warning;
}
