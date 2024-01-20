package org.unicode.conformance.numberformatter;

import static org.junit.Assert.assertEquals;

import org.junit.Test;
import org.unicode.conformance.testtype.numberformatter.NumberFormatterOutputJson;
import org.unicode.conformance.testtype.numberformatter.NumberFormatterTester;

public class NumberFormatterTest {

  @Test
  public void testSkeleton() {
    String testInput =
        "{\"test_type\": \"number_fmt\", \"label\":\"s\", \"pattern\":\"@@@\", \"skeleton\": \"@@@ group-off\", \"input\":\"123456\", \"options\":{}}";

    NumberFormatterOutputJson output =
        (NumberFormatterOutputJson) NumberFormatterTester.INSTANCE.getStructuredOutputFromInputStr(testInput);

    assertEquals("123000", output.result);
  }

}
