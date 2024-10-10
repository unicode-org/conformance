package org.unicode.conformance.testtype.langnames;

import org.unicode.conformance.testtype.ITestTypeInputJson;

public class LangNamesInputJson implements ITestTypeInputJson {

  public String test_type;

  public String label;

  public String language_label;

  public String locale_label;

  public LangNamesDisplayOptions language_display;  // For standard or dialect

}
