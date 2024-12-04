package org.unicode.conformance.collator.icu74;

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

  @Test
  public void testNonEscaped() {
    String testInput =
        "\t{\"label\":\"0006747\",\"s1\":\"̴?\",\"s2\":\"̴̲\",\"line\":5382,\"ignorePunctuation\":true}";

    CollatorOutputJson output =
        (CollatorOutputJson) CollatorTester.INSTANCE.getStructuredOutputFromInputStr(testInput);

    assertTrue(output.result);
  }

  @Test
  public void testAttributesAsArrayList() {
    String testInput =
        "{\"test_type\": \"collation_short\", \"label\":\"00099\",\"s1\":\"\",\"s2\":\"a\",\"line\":293,\"compare_type\":\"&lt;1\",\"test_description\":\" discontiguous contractions\",\"attributes\":[[\"strength\",\"primary\"],[\"strength\",\"secondary\"],[\"strength\",\"tertiary\"],[\"strength\",\"quaternary\"],[\"strength\",\"identical\"]],\"strength\":\"primary\",\"hexhash\":\"4c4c61ac18e9c222aaa457daa5d72a72ce0490d2\"}";

    CollatorOutputJson output =
        (CollatorOutputJson) CollatorTester.INSTANCE.getStructuredOutputFromInputStr(testInput);

    assertTrue(output.result);
  }

/*  @Test
  public void testCompareLT2() {
    String testInput =
        "{\"test_type\": \"collation_short\", \"label\":\"00115\",\"s1\":\"cote\",\"s2\":\"cotÃ©\",\"line\":329,\"source_file\":\"collationtest.txt\",\"compare_type\":\"&lt;2\",\"test_description\":\" discontiguous contractions\",\"hexhash\":\"b56b2f345f58f7044c14e392ea94304c075cbaf5\"}";
    CollatorOutputJson output =
        (CollatorOutputJson) CollatorTester.INSTANCE.getStructuredOutputFromInputStr(testInput);

    assertTrue(output.result);
  }*/
}
