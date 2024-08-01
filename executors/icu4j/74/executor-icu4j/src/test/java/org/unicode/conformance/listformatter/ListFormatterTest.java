package org.unicode.conformance.listformatter;

import static org.junit.Assert.assertEquals;

import org.junit.Test;
import org.unicode.conformance.testtype.listformatter.ListFormatterOutputJson;
import org.unicode.conformance.testtype.listformatter.ListFormatterTester;

public class ListFormatterTest {

  @Test
  public void testEnConjunction() {
      String testInput =
          "\t{\"input_list\":[\"dog\",\"cat\"],\"options\":{\"style\":\"long\",\"list_type\":\"conjunction\"},\"hexhash\":\"9cdda56a2d84e4cecd3f60d1a6f815ad36ea3df9\",\"label\":\"0\",\"locale\":\"en\"}";

              ListFormatterOutputJson output =
        (ListFormatterOutputJson) ListFormatterTester.INSTANCE.getStructuredOutputFromInputStr(testInput);

    assertEquals("dog and cat", output.result);
  }

  @Test
  public void testDeConjunction() {
    String testInput =
    "\t{\"input_list\":[\"katze\",\"hund\"],\"options\":{\"style\":\"long\",\"list_type\":\"disjunction\"},\"hexhash\":\"9cdda56a2d84e4cecd3f60d1a6f815ad36ea3df9\",\"label\":\"0\",\"locale\":\"de\"}";

    ListFormatterOutputJson output =
        (ListFormatterOutputJson) ListFormatterTester.INSTANCE.getStructuredOutputFromInputStr(testInput);

    assertEquals("katze oder hund", output.result);
  }

  @Test
  public void testUndUnit() {
    String testInput =
      "\t{\"input_list\":[\"dog\",\"cat\", \"fish\"],\"options\":{\"style\":\"long\",\"list_type\":\"unit\",\"type\":\"unit\"},\"hexhash\":\"8ea46dfaeb658975ff2f4f7ece1421a504eec5d7\",\"label\":\"18\",\"locale\":\"und\"}";

    ListFormatterOutputJson output =
        (ListFormatterOutputJson) ListFormatterTester.INSTANCE.getStructuredOutputFromInputStr(testInput);

    assertEquals("dog, cat, fish", output.result);
  }
}
