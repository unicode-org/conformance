package org.unicode.conformance.testtype.listformatter;

import java.util.Collection;
import org.unicode.conformance.testtype.ITestTypeInputJson;

public class ListFormatterInputJson implements ITestTypeInputJson {

  public String testType;

  public String label;

  public String locale;

  public ListFormatterType listType;

  public ListFormatterWidth style;  // e.g., SHORT

  public Collection<String> inputList;

}
