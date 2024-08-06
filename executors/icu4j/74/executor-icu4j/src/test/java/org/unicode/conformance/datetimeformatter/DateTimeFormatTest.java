package org.unicode.conformance.datetimeformatter;

import static org.junit.Assert.assertEquals;

import org.junit.Test;

public class DateTimeFormatTest {

  @Test
  public void testDateTime0() {
    String testInput =
        "{\"test_type\":\"datetime_fmt\", \"input_string\":\"2024-03-07T00:00:01+00:00[UTC][u-ca=gregory]\",\"locale\":\"en-US\",\"options\":{\"dateStyle\":\"short\",\"timeStyle\":\"short\",\"calendar\":\"gregory\",\"timeZone\":\"UTC\",\"numberingSystem\":\"latn\"},\"hexhash\":\"048d17f248ef4f6835d6b9b3bcbfdc934f3fcad5\",\"label\":\"0\"}"

    DateTimeFormatterOutputJson output =
        (DateTimeFormatterOutputJson) DateTimeFormattterTester.INSTANCE.getStructuredOutputFromInputStr(
            testInput);

    assertEquals("3/7/24, 12:00 AM", output.result);
  }

  @Test
  public void testDateTime3864() {
    String testInput =
        "{\"test_type\":\"datetime_fmt\",\"input_string\":\"2024-03-07T00:00:01+00:00[UTC][u-ca=gregory]\",\"locale\":\"zh-TW\",\"options\":{\"dateStyle\":\"short\",\"timeStyle\":\"short\",\"calendar\":\"gregory\",\"timeZone\":\"UTC\",\"numberingSystem\":\"latn\"},\"hexhash\":\"2f22cb2c0656fd092d12c17b2545cec4ca9f23b3\",\"label\":\"3864\"}";

    DateTimeFormatterOutputJson output =
        (DateTimeFormatterOutputJson) DateTimeFormattterTester.INSTANCE.getStructuredOutputFromInputStr(
            testInput);

    assertEquals("2024/3/7 凌晨12:00", output.result);
  }

  @Test
  public void testDateTime17387() {

    String textInput = "{\"test_type\":\"datetime_fmt\",\"input_string\":\"2001-09-09T01:46:40+10:00[Australia/Brisbane]\",\"skeleton\":\"vvvv\",\"locale\":\"und\",\"options\":{\"timeZoneName\":\"longGeneric\",\"calendar\":\"persian\",\"timeZone\":\"Australia/Brisbane\",\"numberingSystem\":\"latn\"},\"hexhash\":\"8a39dcac98f0487ead82dedd3447bdf393b35081\",\"label\":\"17387\"}";

    DateTimeFormatterOutputJson output =
        (DateTimeFormatterOutputJson) DateTimeFormattterTester.INSTANCE.getStructuredOutputFromInputStr(
            testInput);

    assertEquals("3/7/24, 12:00 AM", output.result);
  }

}