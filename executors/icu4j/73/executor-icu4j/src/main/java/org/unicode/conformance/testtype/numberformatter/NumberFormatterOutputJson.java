package org.unicode.conformance.testtype.numberformatter;

import java.util.Map;
import org.unicode.conformance.testtype.ITestTypeOutputJson;

public class NumberFormatterOutputJson implements ITestTypeOutputJson {
  String label;

  String result;
  
  public String error;

  public String error_message;
}
