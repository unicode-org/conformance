package org.unicode.conformance.numberformatter.icu74;

import static org.junit.Assert.assertEquals;

import org.junit.Test;
import org.unicode.conformance.testtype.numberformatter.NumberFormatterOutputJson;
import org.unicode.conformance.testtype.numberformatter.NumberFormatterTester;

public class NumberFormatterTest {

  @Test
  public void testSkeleton() {
    String testInput =
        "{\"test_type\": \"number_fmt\", \"label\":\"s\", \"pattern\":\"@@@\", \"skeleton\": \"@@@ group-off\", \"input\":\"123456\", \"options\":{}, \"locale\":\"und\"}";

    NumberFormatterOutputJson output =
        (NumberFormatterOutputJson) NumberFormatterTester.INSTANCE.getStructuredOutputFromInputStr(testInput);

    assertEquals("123000", output.result);
  }

  @Test
  public void testDebug1() {
    String testInput =
        "{ \"label\": \"0146\", \"locale\": \"und\", \"skeleton\": \"compact-short currency/EUR precision-integer\", \"input\": \"-0.22222\", \"options\": { \"notation\": \"compact\", \"compactDisplay\": \"short\", \"style\": \"currency\", \"currencyDisplay\": \"symbol\", \"currency\": \"EUR\", \"maximumFractionDigits\": 0, \"minimumFractionDigits\": 0, \"roundingType\": \"fractionDigits\" }, \"test_type\": \"number_fmt\" }";

    NumberFormatterOutputJson output =
        (NumberFormatterOutputJson) NumberFormatterTester.INSTANCE.getStructuredOutputFromInputStr(testInput);

    assertEquals("-€ 0", output.result);
  }

  @Test
  public void testDebug2() {
    String testInput =
        "{\"label\":\"6497\",\"op\":\"format\",\"pattern\":\"0.0\",\"input\":\"-0.19\",\"options\":{\"roundingMode\":\"expand\",\"minimumIntegerDigits\":1,\"minimumFractionDigits\":1,\"maximumFractionDigits\":1,\"useGrouping\":false}}";

    NumberFormatterOutputJson output =
        (NumberFormatterOutputJson) NumberFormatterTester.INSTANCE.getStructuredOutputFromInputStr(testInput);

    assertEquals("-0.2", output.result);
  }

}
