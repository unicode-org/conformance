package org.unicode.conformance.testtype.listformatter;

import java.util.Collection;

import org.unicode.conformance.testtype.ITestTypeInputJson;

public class ListFormatterInputJson implements ITestTypeInputJson {

  public String test_type;

  public String label;

  public String locale;

  public String list_type;

  public String style;  // e.g., "short

  public Collection<String> input_list;

}
