package org.unicode.conformance.collator;

import static org.junit.Assert.assertTrue;

import org.junit.Test;
import org.unicode.conformance.testtype.collator.CollatorOutputJson;
import org.unicode.conformance.testtype.collator.CollatorTester;

public class CollatorTest {

  @Test
  public void testIgnorePunctuation() {
    String testInput =
        "{\"label\":\"0001424\",\"s1\":\" ?\",\"s2\":\"　?\",\"line\":59,\"ignorePunctuation\":true}";

    CollatorOutputJson output =
        (CollatorOutputJson) CollatorTester.INSTANCE.getStructuredOutputFromInputStr(testInput);

    assertTrue(output.result);

  }

}
