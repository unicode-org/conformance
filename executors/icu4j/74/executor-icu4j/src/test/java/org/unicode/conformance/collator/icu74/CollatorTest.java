package org.unicode.conformance.collator.icu74;

import static org.junit.Assert.assertTrue;

import org.junit.Ignore;
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
        "{\"test_type\": \"collation\", \"label\":\"00099\",\"s1\":\"\",\"s2\":\"a\",\"line\":293,\"compare_type\":\"&lt;1\",\"test_description\":\" discontiguous contractions\",\"attributes\":[[\"strength\",\"primary\"],[\"strength\",\"secondary\"],[\"strength\",\"tertiary\"],[\"strength\",\"quaternary\"],[\"strength\",\"identical\"]],\"strength\":\"primary\",\"hexhash\":\"4c4c61ac18e9c222aaa457daa5d72a72ce0490d2\"}";

    CollatorOutputJson output =
        (CollatorOutputJson) CollatorTester.INSTANCE.getStructuredOutputFromInputStr(testInput);

    assertTrue(output.result);
  }

  @Test
  public void testRule004() {
    // in ICU 76.1 data
    String testInput =
        "{\"test_type\": \"collation\", \"compare_type\":\"&lt;3\",\"s1\":\"\u0002\",\"s2\":\"\u0300\",\"source_file\":\"collationtest.txt\",\"line\":43,\"label\":\"00002\",\"test_description\":\"simple CEs &amp; expansions\",\"rules\":\"&\\u0001<<<\\u0300&9<\\u0000&\\uA00A\\uA00B=\\uA002&\\uA00A\\uA00B\\u00050005=\\uA003\",\"hexhash\":\"7d3d23fab7f34c1cd44e90b40f7ed33c5bb317ba\"}";

    CollatorOutputJson output =
        (CollatorOutputJson) CollatorTester.INSTANCE.getStructuredOutputFromInputStr(testInput);

    assertTrue(output.result);
  }

  @Test
  public void test1362() {
    // in ICU 76.1 data
    String testInput =
        "{\"test_type\": \"collation\", \"compare_type\":\"<2\",\"s1\":\"ae\",\"s2\":\"ä\",\"source_file\":\"collationtest.txt\",\"line\":2426,\"label\":\"01362\",\"localetag\":\"de-u-co-phonebk\", \"locale\": \"de@collation=PhoneBook\",\"test_description\":\"locale @collation=type should be case-insensitive\",\"hexhash\":\"893bdab906f7bc0e918ce388c7e78799d5913eaa\"}";

    CollatorOutputJson output =
        (CollatorOutputJson) CollatorTester.INSTANCE.getStructuredOutputFromInputStr(testInput);

    assertTrue(output.result);
  }

  @Ignore
  @Test
  public void test00144() {
    // in ICU 76.1 data
  String testInput =
      "{\"test_type\": \"collation\", \"compare_type\":\"&lt;2\",\"s1\":\"cote\",\"s2\":\"cotÃ©\",\"source_file\":\"collationtest.txt\",\"line\":329,\"label\":\"00144\",\"locale\":\"root\",\"test_description\":\"côté with forwards secondary\",\"hexhash\":\"9a83942120095cac5793c15daebdf05cf30994ab\"}";

    CollatorOutputJson output =
        (CollatorOutputJson) CollatorTester.INSTANCE.getStructuredOutputFromInputStr(testInput);

    assertTrue(output.result);
  }

@Ignore
@Test
  public void testIdentical() {
    // In ICU 76.1 data
    String testInput = "{\"test_type\": \"collation\",   \"compare_type\": \"=\",   \"s1\": \"a\u0327\",   \"s2\": \"\u00e2\u0093\u0090\u00e2\u009d\u00ba\",   \"source_file\": \"collationtest.txt\",   \"line\": 136,   \"label\": \"00032\",   \"test_description\": \"simple contractions\",   \"rules\": \"&a=\\u00e2\\u0093\\u0090&b<bz=\\u00e2\\u0093\\u0091&d<dz\\u0301=\\u00e2\\u0093\\u0093&z<a\\u0301=\\u00e2\\u0092\\u00b6<a\\u0301\\u0301=\\u00e2\\u0092\\u00b7<a\\u0301\\u0301\\u0358=\\u00e2\\u0092\\u00b8<a\\u030a=\\u00e2\\u0092\\u00b9<a\\u0323=\\u00e2\\u0092\\u00ba<a\\u0323\\u0358=\\u00e2\\u0092\\u00bb<a\\u0327\\u0323\\u030a=\\u00e2\\u0092\\u00bc<a\\u0327\\u0323bz=\\u00e2\\u0092\\u00bd&\\ud834\\udd58=\\u00e2\\u0081\\u00b0<\\ud834\\udd58\\ud834\\udd65=\\u00c2\\u00bc&\\u0001<<<\\ud834\\udd65=\\u00c2\\u00b9<<<\\ud834\\udd6d=\\u00c2\\u00b2<<<\\ud834\\udd65\\ud834\\udd6d=\\u00c2\\u00b3&\\u0301=\\u00e2\\u009d\\u00b6&\\u030a=\\u00e2\\u009d\\u00b7&\\u0308=\\u00e2\\u009d\\u00b8<<\\u0308\\u0301=\\u00e2\\u009d\\u00b9&\\u0327=\\u00e2\\u009d\\u00ba&\\u0323=\\u00e2\\u009d\\u00bb&\\u0331=\\u00e2\\u009d\\u00bc<<\\u0331\\u0358=\\u00e2\\u009d\\u00bd&\\u0334=\\u00e2\\u009d\\u00be&\\u0358=\\u00e2\\u009d\\u00bf&\\u0f71=\\u00e2\\u0091&\\u0f72=\\u00e2\\u0091\\u00a1&\\u0f73=\\u00e2\\u0091\\u00a2\",   \"hexhash\": \"b43889a20872ad4d242f9e94c942cc56cbb89b75\"}";

    CollatorOutputJson output =
        (CollatorOutputJson) CollatorTester.INSTANCE.getStructuredOutputFromInputStr(testInput);

    assertTrue(output.result);
  }

  @Ignore
  @Test
  public void testCompareLT2() {
    String testInput =
        "{\"test_type\": \"collation\", \"label\":\"00115\",\"s1\":\"cote\",\"s2\":\"cotÃ©\",\"line\":329,\"source_file\":\"collationtest.txt\",\"compare_type\":\"&lt;2\",\"test_description\":\" discontiguous contractions\",\"hexhash\":\"b56b2f345f58f7044c14e392ea94304c075cbaf5\"}";
    CollatorOutputJson output =
        (CollatorOutputJson) CollatorTester.INSTANCE.getStructuredOutputFromInputStr(testInput);

    assertTrue(output.result);
  }

  @Test
  public void test00002() {
  String testInput =
      "{\"test_type\": \"collation\", \"compare_type\":\"<3\",\"s1\":\"\u0002\",\"s2\":\"\u0300\",\"source_file\":\"collationtest.txt\",\"line\":43,\"label\":\"00002\",\"test_description\":\"simple CEs & expansions\",\"rules\":\"&\\u0001<<<\\u0300&9<\\u0000&\\uA00A\\uA00B=\\uA002&\\uA00A\\uA00B\\u00050005=\\uA003\",\"hexhash\":\"87be5cda089d675543eb91b948e2d7f74227ff0d\"}";

    CollatorOutputJson output =
        (CollatorOutputJson) CollatorTester.INSTANCE.getStructuredOutputFromInputStr(testInput);

    assertTrue(output.result);
  }

  @Ignore
  @Test
  public void testReorderCodes() {
    String testInput =
        "{\"test_type\": \"collation\", \"compare_type\": \"<1\",\"s1\": \"\",\"s2\": \"?\",\"source_file\": \"collationtest.txt\",\"line\": 397,\"label\": \"00174\",\"locale\": \"root\",\"test_description\": \"script reordering\",\"reorder\": \"Hani Zzzz digit\",\"hexhash\": \"80134ad71a184a3c27f8d4c71a3d74b4561c4445\"}";

        CollatorOutputJson output = (CollatorOutputJson) CollatorTester.INSTANCE.getStructuredOutputFromInputStr(testInput);

        assertTrue(output.result);
  }

  @Test
  public void test01181() {
    // Reordering with Zzzz and Grek
    String testInput =
        "{\"test_type\": \"collation\", \"compare_type\":\"<1\",\"s1\":\"字\",\"s2\":\"Ω\",\"source_file\":\"collationtest.txt\",\"line\":2075,\"label\":\"01181\",\"locale\":\"root\",\"test_description\":\"never reorder trailing primaries\",\"reorder\":\"Zzzz Grek\",\"hexhash\":\"98ed666f1681e88453c101b403e527081bb454b7\"}";
    CollatorOutputJson output = (CollatorOutputJson) CollatorTester.INSTANCE.getStructuredOutputFromInputStr(testInput);

    assertTrue(output.result);
  }

  @Test
  public void testBackwards() {
    // Set locale to fr-CA if backwards option is set.
    String testInput =
        "{\"test_type\": \"collation\", \"compare_type\":\"<2\",\"s1\":\"côte\",\"s2\":\"coté\",\"source_file\":\"collationtest.txt\",\"line\":347,\"label\":\"00153\",\"locale\":\"root\",\"test_description\":\"côté with backwards secondary\",\"backwards\":\"on\",\"hexhash\":\"0054321a336610ec2eabc4e824736e7e886bab4d\"}";

    CollatorOutputJson output = (CollatorOutputJson) CollatorTester.INSTANCE.getStructuredOutputFromInputStr(testInput);

    assertTrue(output.result);
  }

  @Test
  public void testHandleNullCharacter() {
    // Handle null character in string
    String testInput =
        "{\"test_type\": \"collation\",    \"compare_type\": \"<1\",   \"s1\": \"9\",   \"s2\": \"\\u0000\",   \"source_file\": \"collationtest.txt\",   \"line\": 45,   \"label\": \"00004\",   \"test_description\": \"simple CEs & expansions\",   \"rules\": \"&\\u0001<<<\\u0300&9<\u0000&\uA00A\uA00B=\uA002&\uA00A\uA00B\u00050005=\uA003\",   \"hexhash\": \"640c05d364b05f3329dd7c17f7ec229e632cc312\"}";

    CollatorOutputJson output = (CollatorOutputJson) CollatorTester.INSTANCE.getStructuredOutputFromInputStr(testInput);

    assertTrue(output.result);
  }

@Test
  public void testUnescapeX() {
    String testInput =
        "{\"test_type\": \"collation\", \"compare_type\":\"=\",\"s1\":\"\",\"s2\":\"\\u0001\",\"source_file\":\"collationtest.txt\",\"line\":41,\"label\":\"00000\",\"test_description\":\"simple CEs & expansions\",\"rules\":\"&\\\\x01<<<\\\\u0300&9<\\\\x00&\\\\uA00A\\\\uA00B=\\\\uA002&\\\\uA00A\\\\uA00B\\\\u00050005=\\\\uA003\",\"hexhash\":\"2f12126264afe7896a48c115f890c292a8cc4f30\"}";

    CollatorOutputJson output = (CollatorOutputJson) CollatorTester.INSTANCE.getStructuredOutputFromInputStr(testInput);

    assertTrue(output.result);
  }

  @Test
  public void testSHIFTED_SHORT() {
    // Unexpected test failure
    String testInput =
        "{\"test_type\": \"collation\", \"label\":\"0004624\",\"s1\":\"／?\",\"s2\":\"\\\\!\",\"strength\":\"tertiary\",\"line\":3185,\"source_file\":\"CollationTest_SHIFTED_SHORT.txt\",\"ignorePunctuation\":true,\"hexhash\":\"03116a4cfdeb7812cbe4aed927009e4bb7962758\"}";

    CollatorOutputJson output = (CollatorOutputJson) CollatorTester.INSTANCE.getStructuredOutputFromInputStr(testInput);

    assertTrue(output.result);
  }
}

