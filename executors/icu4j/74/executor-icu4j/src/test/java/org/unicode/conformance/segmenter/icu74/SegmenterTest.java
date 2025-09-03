package org.unicode.conformance.segmenter.icu74;

import static org.hamcrest.CoreMatchers.is;
import static org.junit.Assert.assertThat;

import java.util.List;
import java.util.Arrays;
import org.junit.Test;

import org.unicode.conformance.testtype.segmenter.SegmenterOutputJson;
import org.unicode.conformance.testtype.segmenter.SegmenterTester;

public class SegmenterTest {

  @Test
  public void testEnGraphemeCluster() {
    String testInput =
        "\t{\"locale\":\"en-US\",\"options\":{\"granularity\":\"grapheme_cluster\"},\"input\":\"The cat;\",\"hexhash\":\"123\",\"label\":\"000\"}";
    SegmenterOutputJson output =
        (SegmenterOutputJson) SegmenterTester.INSTANCE.getStructuredOutputFromInputStr(testInput);
    List<String> expected = Arrays.asList("T",  "h", "e", " ", "c", "a", "t", ";");
    assertThat(expected, is(output.result));
  }

  @Test
  public void testEnWord() {
    String testInput =
        "\t{\"locale\":\"en-US\",\"options\":{\"granularity\":\"word\"},\"input\":\"The cat;\",\"hexhash\":\"123\",\"label\":\"000\"}";
    SegmenterOutputJson output =
        (SegmenterOutputJson) SegmenterTester.INSTANCE.getStructuredOutputFromInputStr(testInput);
    List<String> expected = Arrays.asList("The", " ", "cat", ";");
    assertThat(expected, is(output.result));
  }

  @Test
  public void testEnSentence() {
    String testInput =
        "\t{\"locale\":\"en-US\",\"options\":{\"granularity\":\"sentence\"},\"input\":\"The cat. A dog.\",\"hexhash\":\"123\",\"label\":\"000\"}";
    SegmenterOutputJson output =
        (SegmenterOutputJson) SegmenterTester.INSTANCE.getStructuredOutputFromInputStr(testInput);
    List<String> expected = Arrays.asList("The cat. ", "A dog.");
    assertThat(expected, is(output.result));
  }

  @Test
  public void testEnLine() {
    String testInput =
        "\t{\"locale\":\"en-US\",\"options\":{\"granularity\":\"line\"},\"input\":\"The cat. A dog.\",\"hexhash\":\"123\",\"label\":\"000\"}";
    SegmenterOutputJson output =
        (SegmenterOutputJson) SegmenterTester.INSTANCE.getStructuredOutputFromInputStr(testInput);
    List<String> expected = Arrays.asList("The ", "cat. ", "A ", "dog.");
    assertThat(expected, is(output.result));
  }
}
