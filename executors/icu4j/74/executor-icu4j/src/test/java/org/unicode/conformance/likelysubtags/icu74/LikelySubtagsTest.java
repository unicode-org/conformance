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

/*  @Test
  public void testUndLatnRS() {
    String testInput =
        "{\"test_type\": \"likely_subtags\", \"label\":\"4350\",\"locale\":\"und-Latn-RS\",\"option\":\"maximize\"}";

    LikelySubtagsOutputJson output =
        (LikelySubtagsOutputJson) LikelySubtagsTester.INSTANCE.getStructuredOutputFromInputStr(testInput);

    assertEquals("sr-Latn", output.result);
  }*/
}
