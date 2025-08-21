package org.unicode.conformance.numberformatter.icu74;

import static org.junit.Assert.assertEquals;

import java.util.regex.Matcher;
import java.util.regex.Pattern;
import org.junit.Ignore;
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

  @Test
  public void testDebugBadPattern() {
    String testInput = "{\"test_type\": \"number_fmt\", \"label\":\"5865\",\"op\":\"format\",\"pattern\":\"00.##E0\",\"input\":\"1234567\",\"options\":{\"roundingMode\":\"halfEven\",\"notation\":\"scientific\",\"minimumIntegerDigits\":2,\"minimumFractionDigits\":1,\"maximumFractionDigits\":3,\"useGrouping\":false},\"hexhash\":\"bbaf139c38c5be2b1028124e8da7f1497b19d0a3\"}";

    NumberFormatterOutputJson output =
        (NumberFormatterOutputJson) NumberFormatterTester.INSTANCE.getStructuredOutputFromInputStr(testInput);

    assertEquals("unsupported pattern", output.unsupported);
  }

  @Test
  public void testRoundingUnnecesary() {
    String testInput = "{\"test_type\": \"number_fmt\", \"label\":\"5919\",\"op\":\"format\",\"pattern\":\"0.00\",\"skeleton\":\".00 rounding-mode-unnecessary\",\"input\":\"-32.045\",\"options\":{\"roundingMode\":\"unnecessary\",\"minimumIntegerDigits\":1,\"minimumFractionDigits\":2,\"maximumFractionDigits\":2,\"useGrouping\":false},\"hexhash\":\"bbbd9b3299dab2d42ea10ea0b068680b99aef9b1\"}";
    NumberFormatterOutputJson output =
        (NumberFormatterOutputJson) NumberFormatterTester.INSTANCE.getStructuredOutputFromInputStr(testInput);

    Pattern check_error = Pattern.compile("Rounding is required");
    Matcher matcher_error = check_error.matcher(output.error);
    assertEquals(matcher_error.find(), true);
  }

  @Test
  public void testRoundingHalfOdd() {
    String testInput =
"{\"test_type\": \"number_fmt\", \"label\":\"5927\",\"op\":\"format\",\"pattern\":\"0.00\",\"skeleton\":\".00 rounding-mode-half-odd\",\"input\":\"1.235\",\"options\":{\"roundingMode\":\"halfOdd\",\"minimumIntegerDigits\":1,\"minimumFractionDigits\":2,\"maximumFractionDigits\":2,\"useGrouping\":false},\"hexhash\":\"0f81db6894d53d8bb8973e658acc50726ae11295\"}";

    NumberFormatterOutputJson output =
        (NumberFormatterOutputJson) NumberFormatterTester.INSTANCE.getStructuredOutputFromInputStr(testInput);

    assertEquals("rounding-mode-half-odd", output.error_detail);
  }

  @Test
  public void testPrecisionIncrement() {
    String testInput =
        "{\"test_type\": \"number_fmt\", \"label\":\"5868\",\"op\":\"format\",\"pattern\":\"0005\",\"skeleton\":\"integer-width/0000 precision-increment/0005 group-off rounding-mode-half-even\",\"input\":\"1234\",\"options\":{\"roundingMode\":\"halfEven\",\"minimumIntegerDigits\":4,\"roundingIncrement\":5,\"maximumFractionDigits\":0,\"roundingPriority\":\"auto\",\"useGrouping\":false},\"hexhash\":\"1fd49a0510450f4c3cc4dd7a33072488ac9e12ad\"}";

    NumberFormatterOutputJson output =
        (NumberFormatterOutputJson) NumberFormatterTester.INSTANCE.getStructuredOutputFromInputStr(testInput);

    assertEquals("1235", output.result);
  }

}
