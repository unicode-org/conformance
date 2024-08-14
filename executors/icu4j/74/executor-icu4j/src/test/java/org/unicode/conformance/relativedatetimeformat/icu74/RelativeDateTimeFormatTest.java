package org.unicode.conformance.relativedatetimeformat.icu74;

import static org.junit.Assert.assertEquals;

import org.junit.Ignore;
import org.junit.Test;
import org.unicode.conformance.testtype.relativedatetimeformat.RelativeDateTimeFormatOutputJson;
import org.unicode.conformance.testtype.relativedatetimeformat.RelativeDateTimeFormatTester;

public class RelativeDateTimeFormatTest {

  @Test
  public void testEn100SecondsAgo() {
    String testInput =
        "\t{\"unit\":\"second\",\"count\":\"-100\",\"locale\":\"en-US\",\"options\":{},\"hexhash\":\"ab5dfa48d57aac79202e8e4dfd12b729b8e4a74a\",\"label\":\"0\"}";

    RelativeDateTimeFormatOutputJson output =
        (RelativeDateTimeFormatOutputJson) RelativeDateTimeFormatTester.INSTANCE.getStructuredOutputFromInputStr(
            testInput);

    assertEquals("100 seconds ago", output.result);
  }

  @Test
  public void testEnIn100Sec() {
    String testInput =
        "\t{\"unit\":\"second\",\"count\":\"100\",\"locale\":\"en-US\",\"options\":{\"style\":\"short\"},\"hexhash\":\"ab5dfa48d57aac79202e8e4dfd12b729b8e4a74a\",\"label\":\"0\"}";

    RelativeDateTimeFormatOutputJson output =
        (RelativeDateTimeFormatOutputJson) RelativeDateTimeFormatTester.INSTANCE.getStructuredOutputFromInputStr(
            testInput);

    assertEquals("in 100 sec.", output.result);
  }

  @Test
  public void testEnIn100Seconds() {
    String testInput =
        "\t{\"unit\":\"second\",\"count\":\"100\",\"locale\":\"en-US\",\"options\":{\"style\":\"long\"},\"hexhash\":\"ab5dfa48d57aac79202e8e4dfd12b729b8e4a74a\",\"label\":\"0\"}";

    RelativeDateTimeFormatOutputJson output =
        (RelativeDateTimeFormatOutputJson) RelativeDateTimeFormatTester.INSTANCE.getStructuredOutputFromInputStr(
            testInput);

    assertEquals("in 100 seconds", output.result);
  }

  @Test
  public void testEn100SecAgo() {
    String testInput =
        "\t{\"unit\":\"second\",\"count\":\"-100\",\"locale\":\"en-US\",\"options\":{\"style\":\"short\"},\"hexhash\":\"ab5dfa48d57aac79202e8e4dfd12b729b8e4a74a\",\"label\":\"0\"}";

    RelativeDateTimeFormatOutputJson output =
        (RelativeDateTimeFormatOutputJson) RelativeDateTimeFormatTester.INSTANCE.getStructuredOutputFromInputStr(
            testInput);

    assertEquals("100 sec. ago", output.result);
  }

  @Test
  public void testEn100SAgo() {
    String testInput =
        "\t{\"unit\":\"second\",\"count\":\"-100\",\"locale\":\"en-US\",\"options\":{\"style\":\"narrow\"},\"hexhash\":\"a57aac792\",\"label\":\"0\"}";

    RelativeDateTimeFormatOutputJson output =
        (RelativeDateTimeFormatOutputJson) RelativeDateTimeFormatTester.INSTANCE.getStructuredOutputFromInputStr(
            testInput);

    assertEquals("100s ago", output.result);
  }

  @Ignore
  // This doesn't yet handle non-ASCII numbering systems
  // https://github.com/unicode-org/conformance/issues/261
  @Test
  public void testAdlamIn1Year() {
    // Adlam string in output
    //
    String testInput =
        "\t{\"unit\":\"second\",\"count\":\"-100\",\"locale\":\"en-US\",\"options\":{\"style\":\"narrow\"},\"numberingSystem\":\"adlm\",\"hexhash\":\"79202e8e\",\"label\":\"0\"}";

    RelativeDateTimeFormatOutputJson output =
        (RelativeDateTimeFormatOutputJson) RelativeDateTimeFormatTester.INSTANCE.getStructuredOutputFromInputStr(
            testInput);

    assertEquals("in 𞥑𞥐y", output.result);
  }

  @Test
  public void testArabicNumSystem() {

  // Expect Eastern Arabic numerals in the output
  String testInput =
      "\t{\"test_type\": \"rdt_fmt\", \"unit\":\"second\",\"count\":\"-100\",\"locale\":\"en-US\",\"options\":{\"numberingSystem\":\"arab\"},\"hexhash\":\"d12df88777f8c7f60130df51d2954e18ec42b9c8\",\"label\":\"704\"}";

  RelativeDateTimeFormatOutputJson output =
      (RelativeDateTimeFormatOutputJson) RelativeDateTimeFormatTester.INSTANCE.getStructuredOutputFromInputStr(
          testInput);

  assertEquals("١٠٠ seconds ago",output.result);
}

}
