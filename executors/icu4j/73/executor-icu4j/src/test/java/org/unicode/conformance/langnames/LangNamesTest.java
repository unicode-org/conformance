package org.unicode.conformance.langnames;

import static org.junit.Assert.assertEquals;

import org.junit.Test;
import org.unicode.conformance.testtype.langnames.LangNamesOutputJson;
import org.unicode.conformance.testtype.langnames.LangNamesTester;

public class LangNamesTest {

  @Test
  public void testLocaleAndDisplayLocale() {
    String testInput =
        "{\"test_type\": \"lang_names\", \"label\": \"01\", \"language_label\": \"fr\", \"locale_label\": \"de\"}";

    LangNamesOutputJson output =
        (LangNamesOutputJson) LangNamesTester.INSTANCE.getStructuredOutputFromInputStr(testInput);

    assertEquals("Französisch", output.result);
  }

}
