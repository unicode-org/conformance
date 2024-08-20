package org.unicode.conformance.testtype.relativedatetimeformat;

import org.unicode.conformance.testtype.ITestTypeInputJson;

public class RelativeDateTimeFormatInputJson implements ITestTypeInputJson {

  public String test_type;

  public String label;

  public String locale;

  public String numberingSystem;

  public RelativeDateFormatNumeric numeric;// always (default) or auto

  public String count;

  public RelativeDateTimeFormatUnits unit;

  public RelativeDateTimeFormatStyle style;  // E.g., SHORT

  public double quantity;
}
