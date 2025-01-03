package org.unicode.conformance.testtype.messageformat2;

import java.time.LocalDateTime;
import java.time.ZoneOffset;
import java.time.format.DateTimeFormatter;
import java.util.Date;

public class MFInputParamDatetime implements IMFInputParam {
  public String name;

  public Date value;

  public MFInputParamDatetime(String name, String datetimeStr) {
    this.name = name;

    LocalDateTime ldt = LocalDateTime.parse(datetimeStr, DateTimeFormatter.ISO_DATE_TIME);
    this.value = Date.from(ldt.atZone(ZoneOffset.UTC).toInstant());;
  }

  @Override
  public String getName() {
    return name;
  }

  @Override
  public Object getValue() {
    return value;
  }
}
