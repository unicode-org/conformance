package org.unicode.conformance.pluralrules;

import static org.junit.Assert.assertEquals;

import org.junit.Test;
import org.unicode.conformance.testtype.pluralrules.PluralRulesOutputJson;
import org.unicode.conformance.testtype.pluralrules.PluralRulesTester;
public class PluralRulesTest {

  @Test
  public void testEnOne() {
    String testInput =
        "{\t\"locale\": \"en\", \"label\": \"en1\", \"plural_type\": \"cardinal\", \"sample\": \"1\", \"hexhash\": \"0d045ce8\"}";

    PluralRulesOutputJson output =
        (PluralRulesOutputJson) PluralRulesTester.INSTANCE.getStructuredOutputFromInputStr(testInput);

    assertEquals("one", output.result);
  }

  @Test
  public void testEnOneOrdinal() {
    String testInput =
        "{\t\"locale\": \"en\", \"label\": \"en1Oridinal\", \"plural_type\": \"ordinal\", \"sample\": \"1\", \"hexhash\": \"0d045ce8\"}";

    PluralRulesOutputJson output =
        (PluralRulesOutputJson) PluralRulesTester.INSTANCE.getStructuredOutputFromInputStr(testInput);

    assertEquals("one", output.result);
  }

  @Test
  public void testFrOne() {
    String testInput =
        "{\t\"locale\": \"fr\", \"label\": \"fr0\", \"plural_type\": \"cardinal\", \"sample\": \"0\", \"hexhash\": \"0d045ce9\"}";

    PluralRulesOutputJson output =
        (PluralRulesOutputJson) PluralRulesTester.INSTANCE.getStructuredOutputFromInputStr(testInput);

    assertEquals("one", output.result);
  }

  @Test
  public void tesCyOther() {
    String testInput =
        "{\t\"locale\": \"cy\", \"label\": \"en0\", \"plural_type\": \"cardinal\", \"sample\": \"0\", \"hexhash\": \"0d045ce9\"}";

    PluralRulesOutputJson output =
        (PluralRulesOutputJson) PluralRulesTester.INSTANCE.getStructuredOutputFromInputStr(testInput);

    assertEquals("zero", output.result);
  }
  
  @Test
  public void testEnOther() {
    String testInput =
        "{\t\"locale\": \"en\", \"label\": \"en17\", \"plural_type\": \"cardinal\", \"sample\": \"17\", \"hexhash\": \"0d045ce9\"}";

    PluralRulesOutputJson output =
        (PluralRulesOutputJson) PluralRulesTester.INSTANCE.getStructuredOutputFromInputStr(testInput);

    assertEquals("other", output.result);
  }

  @Test
  public void testBmOther() {
    String testInput =
        "{\t\"locale\": \"bm\", \"label\": \"bm1\", \"plural_type\": \"cardinal\", \"sample\": \"1\", \"hexhash\": \"0d045ce9\"}";

    PluralRulesOutputJson output =
        (PluralRulesOutputJson) PluralRulesTester.INSTANCE.getStructuredOutputFromInputStr(testInput);

    assertEquals("other", output.result);
  }

  @Test
  public void testIuOther() {
    String testInput =
        "{\t\"locale\": \"iu\", \"label\": \"iu3495\", \"plural_type\": \"cardinal\", \"sample\": \"2.0\", \"hexhash\": \"0d045ce9\"}";

    PluralRulesOutputJson output =
        (PluralRulesOutputJson) PluralRulesTester.INSTANCE.getStructuredOutputFromInputStr(testInput);

    assertEquals("two", output.result);
  }

  @Test
  public void testFrManyOther() {
    String testInput =
        "{\t\"locale\": \"fr\", \"label\": \"4007\", \"plural_type\": \"cardinal\", \"sample\": \"1000000\", \"hexhash\": \"8dd05e1e6479f1d8ce7e261d94d22b96e1d01238\"}";

    PluralRulesOutputJson output =
        (PluralRulesOutputJson) PluralRulesTester.INSTANCE.getStructuredOutputFromInputStr(testInput);

    assertEquals("many", output.result);
  }
}
