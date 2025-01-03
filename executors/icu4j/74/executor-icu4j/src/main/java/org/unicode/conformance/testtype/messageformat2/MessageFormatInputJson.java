package org.unicode.conformance.testtype.messageformat2;

import java.util.List;
import org.unicode.conformance.testtype.ITestTypeInputJson;

public class MessageFormatInputJson implements ITestTypeInputJson {

  public String label;

  public String locale;

  public String src;

  public String test_description;

  public List<IMFInputParam> params;

  public String verify;

}
