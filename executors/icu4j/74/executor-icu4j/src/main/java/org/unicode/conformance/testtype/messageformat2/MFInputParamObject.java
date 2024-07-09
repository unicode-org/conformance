package org.unicode.conformance.testtype.messageformat2;

public class MFInputParamObject implements IMFInputParam {

  public String name;

  public Object value;

  @Override
  public String getName() {
    return this.name;
  }

  @Override
  public Object getValue() {
    return this.value;
  }
}
