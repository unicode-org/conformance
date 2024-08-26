package org.unicode.conformance.langnames.icu74;

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

  @Test
  public void testLocaleNameStandardDutchBelgium() {
    String testInput =
        "{\"test_type\": \"lang_names\", \"label\": \"nl1\", \"language_label\": \"nl-BE\", \"locale_label\": \"en\", \"languageDisplay\": \"standard\"}";

    LangNamesOutputJson output =
        (LangNamesOutputJson) LangNamesTester.INSTANCE.getStructuredOutputFromInputStr(testInput);

    assertEquals("Dutch (Belgium)", output.result);
  }

  @Test
  public void testLocaleNameDialectFlemish() {
    String testInput =
        "{\"test_type\": \"lang_names\", \"label\": \"nl2\", \"language_label\": \"nl-BE\", \"locale_label\": \"en\", \"languageDisplay\": \"dialect\"}";

    LangNamesOutputJson output =
        (LangNamesOutputJson) LangNamesTester.INSTANCE.getStructuredOutputFromInputStr(testInput);

    assertEquals("Flemish", output.result);
  }

}
