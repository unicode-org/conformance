package org.unicode.conformance.relativedatetimeformat;

import static org.junit.Assert.assertEquals;

import org.junit.Test;
import org.unicode.conformance.testtype.pluralrules.PluralRulesOutputJson;
import org.unicode.conformance.testtype.pluralrules.PluralRulesTester;
import org.unicode.conformance.testtype.pluralrules.RelativeDateTimeFormatOutputJson;
import org.unicode.conformance.testtype.pluralrules.RelativeDateTimeFormatTester;
public class RelativeDateTimeFormatTest {

  @Test
  public void testEn100SecondsAgo() {
    String testInput =
        "\t{\"unit\":\"second\",\"count\":\"-100\",\"locale\":\"en-US\",\"options\":{},\"hexhash\":\"ab5dfa48d57aac79202e8e4dfd12b729b8e4a74a\",\"label\":\"0\"}";

    PluralRulesOutputJson output =
        (PluralRulesOutputJson) PluralRulesTester.INSTANCE.getStructuredOutputFromInputStr(testInput);

    assertEquals("100 seconds ago", output.result);
  }
}
