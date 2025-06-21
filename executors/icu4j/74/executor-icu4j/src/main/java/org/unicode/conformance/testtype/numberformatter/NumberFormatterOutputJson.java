package org.unicode.conformance.testtype.numberformatter;

import java.util.Map;
import org.unicode.conformance.testtype.ITestTypeOutputJson;

public class NumberFormatterOutputJson implements ITestTypeOutputJson {
  public String label;

  public String result;

  public String unsupported;
  public String error;
  public String error_detail;
  public String error_type;
  public String error_message;
}

