package org.unicode.conformance.datetimeformatter;

import org.junit.Ignore;
import static org.junit.Assert.assertEquals;

import org.junit.Test;
import org.unicode.conformance.testtype.datetimeformatter.DateTimeFormatterOutputJson;
import org.unicode.conformance.testtype.datetimeformatter.DateTimeFormatterTester;

public class DateTimeFormatterTest {

  @Test
  public void TestDateTime49() {
    String testInput =
        "{\"test_type\": \"datetime_fmt\", \"input_string\":\"2024-03-07T00:00:01.00Z[u-ca=gregory]\","
            +
            "\"skeleton\":\"j\",\"locale\":\"en-US\",\"options\":{\"hour\":\"numeric\",\"calendar\":\"gregory\","
            +
            "\"timeZone\":\"America/Los_Angeles\",\"numberingSystem\":\"latn\"},\"hexhash\":\"30c5191c8041eb6d8afa05aab80f811753bc082f\",\"label\":\"49\"}";

    DateTimeFormatterOutputJson output =
        (DateTimeFormatterOutputJson) DateTimeFormatterTester.INSTANCE.getStructuredOutputFromInputStr(
            testInput);
    assertEquals("12 AM", output.result);
  }

  @Test
  public void TestDateTime15455() {
    String testInput =
        "{\"test_type\": \"datetime_fmt\", \"input_string\":\"2001-09-09T01:46:40.00Z\"," +
            "\"skeleton\":\"vvvv\",\"locale\":\"zu\",\"options\":{\"timeZoneName\":\"longGeneric\","
            +
            "\"calendar\":\"persian\",\"timeZone\":\"America/Los_Angeles\",\"numberingSystem\":\"latn\"},"
            +
            "\"hexhash\":\"d4cfde2db66f8d4aec9254fc66ef2db298d7a0ba\",\"label\":\"15455\"}";

    DateTimeFormatterOutputJson output =
        (DateTimeFormatterOutputJson) DateTimeFormatterTester.INSTANCE.getStructuredOutputFromInputStr(
            testInput);
    assertEquals("Isikhathi sase-North American Pacific", output.result);
  }

  @Test
  public void testDateTime0x() {
    String testInput =
        "{\"test_type\":\"datetime_fmt\", \"input_string\":\"2024-03-07T00:00:01.00Z[UTC][u-ca=gregory]\","
            +
            "\"locale\":\"en-US\",\"options\":{\"dateStyle\":\"short\",\"timeStyle\":\"short\"," +
            "\"calendar\":\"gregory\",\"timeZone\":\"UTC\",\"numberingSystem\":\"latn\"}," +
            "\"hexhash\":\"048d17f248ef4f6835d6b9b3bcbfdc934f3fcad5\",\"label\":\"0\"}";

    DateTimeFormatterOutputJson output =
        (DateTimeFormatterOutputJson) DateTimeFormatterTester.INSTANCE.getStructuredOutputFromInputStr(
            testInput);

    assertEquals("3/7/24, 12:00 AM", output.result);
  }

  @Test
  public void testDateTime3864() {
    String testInput =
        "{\"test_type\":\"datetime_fmt\",\"input_string\":\"2024-03-07T00:00:12.00Z[UTC][u-ca=gregory]\","
            +
            "\"locale\":\"zh-TW\",\"options\":{\"dateStyle\":\"short\",\"timeStyle\":\"short\"," +
            "\"calendar\":\"gregory\",\"timeZone\":\"UTC\",\"numberingSystem\":\"latn\"}," +
            "\"hexhash\":\"2f22cb2c0656fd092d12c17b2545cec4ca9f23b3\",\"label\":\"3864\"}";

    DateTimeFormatterOutputJson output =
        (DateTimeFormatterOutputJson) DateTimeFormatterTester.INSTANCE.getStructuredOutputFromInputStr(
            testInput);

    assertEquals("2024/3/7 凌晨12:00", output.result);
  }

  @Test
  public void testDateTime17387() {
    String testInput =
        "\t{\"test_type\":\"datetime_fmt\",\"input_string\":\"2001-09-09T01:46:40.01Z\"," +
            "\"skeleton\":\"vvvv\",\"locale\":\"en\",\"options\":{\"timeZoneName\":\"longGeneric\","
            +
            "\"calendar\":\"persian\",\"timeZone\":\"Australia/Brisbane\",\"numberingSystem\":\"latn\"},"
            +
            "\"hexhash\":\"8a39dcac98f0487ead82dedd3447bdf393b35081\",\"label\":\"17387\"}";

    DateTimeFormatterOutputJson output =
        (DateTimeFormatterOutputJson) DateTimeFormatterTester.INSTANCE.getStructuredOutputFromInputStr(
            testInput);

    assertEquals("Australian Eastern Standard Time", output.result);
  }

  @Test
  public void testDateTime5126() {
    String testInput =
        "\t{\"test_type\": \"datetime_fmt\", \"input_string\":\"1984-05-29T07:53:00.01Z\"," +
            "\"skeleton\": \"OOOO\",\"locale\":\"zh-TW\",\"options\":{\"timeZoneName\":\"longOffset\"," +
            "\"calendar\":\"japanese\",\"timeZone\":\"Europe/Kiev\",\"numberingSystem\":\"latn\"}," +
            "\"hexhash\":\"f44d2a93e473d0ead6b008a33aad3d2a93a2aa3c\",\"label\":\"5126\"}";

    DateTimeFormatterOutputJson output =
        (DateTimeFormatterOutputJson) DateTimeFormatterTester.INSTANCE.getStructuredOutputFromInputStr(
            testInput);

    assertEquals("GMT+04:00", output.result);
  }

  @Test
  public void testDateTime0() {
    String testInput = "\t{\"test_type\": \"datetime_fmt\", \"input_string\":\"2024-03-07T00:00:01.00Z[UTC][u-ca=gregory]\"," +
        "\"locale\":\"en-US\",\"options\":{\"dateStyle\":\"short\",\"timeStyle\":\"short\",\"calendar\":\"gregory\"," +
        "\"timeZone\":\"UTC\",\"numberingSystem\":\"latn\"},\"hexhash\":\"048d17f248ef4f6835d6b9b3bcbfdc934f3fcad5\",\"label\":\"0\"}";

    DateTimeFormatterOutputJson output =
        (DateTimeFormatterOutputJson) DateTimeFormatterTester.INSTANCE.getStructuredOutputFromInputStr(
            testInput);

    assertEquals("3/7/24, 12:00 AM", output.result);
  }

  @Test
  public void testDate35() {
    String testInput =
    "\t{\"test_type\": \"datetime_fmt\"," +
        "\"input_string\":\"2024-03-07T00:00:01.00Z[UTC][u-ca=gregory]\"," +
        "\"locale\":\"en-US\"," +
        "\"options\":{\"dateStyle\":\"long\",\"calendar\":\"gregory\",\"timeZone\":\"Asia/Tehran\",\"numberingSystem\":\"latn\"}," +
        "\"hexhash\":\"27b3476384c651ce0812edd378f127c1b3eb1dae\",\"label\":\"35\"}";

    DateTimeFormatterOutputJson output =
        (DateTimeFormatterOutputJson) DateTimeFormatterTester.INSTANCE.getStructuredOutputFromInputStr(
            testInput);

    assertEquals("3/7/24", output.result);
  }

  @Test
  public void testDate217() {
    String testInput =
        "\t{\"test_type\": \"datetime_fmt\", \"input_string\":\"2024-03-07T00:00:01.00Z[UTC][u-ca=gregory]\"," +
            "\"locale\":\"en-US\"," +
            "\"options\":{\"dateStyle\":\"short\",\"timeStyle\":\"short\",\"calendar\":\"buddhist\",\"timeZone\":\"America/Los_Angeles\",\"numberingSystem\":\"latn\"}," +
            "\"hexhash\":\"d099e6a6a45df0ce89f1e60d9d5caa85fc64da28\",\"label\":\"217\"}";

    DateTimeFormatterOutputJson output =
        (DateTimeFormatterOutputJson) DateTimeFormatterTester.INSTANCE.getStructuredOutputFromInputStr(
            testInput);

    assertEquals("3/6/2567 BE, 4:00 PM", output.result);
  }
}