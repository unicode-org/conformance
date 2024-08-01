package org.unicode.conformance.testtype.listformatter;

import java.util.Collection;
import org.unicode.conformance.testtype.ITestTypeInputJson;

public class ListFormatterInputJson implements ITestTypeInputJson {

  public String test_type;

  public String label;

  public String locale;

  public ListFormatterType list_type;

  public ListFormatterWidth style;  // e.g., SHORT

  public Collection<String> input_list;

}
