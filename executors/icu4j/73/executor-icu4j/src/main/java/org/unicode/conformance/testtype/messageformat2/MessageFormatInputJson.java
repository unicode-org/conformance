package org.unicode.conformance.testtype.messageformat2;

import java.util.List;
import org.unicode.conformance.testtype.ITestTypeInputJson;

public class MessageFormatInputJson implements ITestTypeInputJson {

  public String test_type;

  public String label;

  public MFTestSubType test_subtype;

  public String locale;

  public String pattern;

  public String test_description;

  public List<MFInputArg> inputs;

  public String verify;

}
