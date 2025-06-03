package org.unicode.conformance.testtype.segmenter;

import java.util.Collection;
import org.unicode.conformance.testtype.ITestTypeInputJson;

public class SegmenterInputJson implements ITestTypeInputJson {

  public String testType;

  public String label;

  public String locale;

  public SegmenterType segmenterType;

  public String inputString;
}
