package org.unicode.conformance.likelysubtags.icu74;

import static org.junit.Assert.assertEquals;

import org.junit.Test;
import org.unicode.conformance.testtype.likelysubtags.LikelySubtagsOutputJson;
import org.unicode.conformance.testtype.likelysubtags.LikelySubtagsTester;

public class LikelySubtagsTest {

  @Test
  public void testMinimizeSubtags() {
    String testInput =
        "{\"test_type\":\"likely_subtags\", \"option\":\"minimize\", \"locale\":\"fr-Latn-FR\", \"label\":\"1\"}";

    LikelySubtagsOutputJson output =
        (LikelySubtagsOutputJson) LikelySubtagsTester.INSTANCE.getStructuredOutputFromInputStr(testInput);

    assertEquals("fr", output.result);
  }

  @Test
  public void testMaximizeSubtags() {
    String testInput =
        "{\"test_type\":\"likely_subtags\", \"option\":\"maximize\", \"locale\":\"fr\", \"label\":\"1\"}";

    LikelySubtagsOutputJson output =
        (LikelySubtagsOutputJson) LikelySubtagsTester.INSTANCE.getStructuredOutputFromInputStr(testInput);

    assertEquals("fr-Latn-FR", output.result);
  }

  @Test
  public void testFailQaa() {
    String testInput =
        "{\"test_type\": \"likely_subtags\", \"label\":\"2412\",\"locale\":\"qaa\",\"option\":\"maximize\",\"hexhash\":\"0135bf6b9b2e3fb98d451d5476a7969c2d3332a4\"}";
    LikelySubtagsOutputJson output =
        (LikelySubtagsOutputJson) LikelySubtagsTester.INSTANCE.getStructuredOutputFromInputStr(testInput);

    assertEquals("FAIL", output.result);
  }
}
