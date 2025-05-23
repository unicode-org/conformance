package org.unicode.conformance.testtype.segmenter;

import java.util.List;
import org.unicode.conformance.testtype.ITestTypeOutputJson;

import java.util.Arrays;

public class SegmenterOutputJson implements ITestTypeOutputJson {

  public String test_type;

  public String label;

  public List<String> result;

  public String error;

  public String error_message;
}
