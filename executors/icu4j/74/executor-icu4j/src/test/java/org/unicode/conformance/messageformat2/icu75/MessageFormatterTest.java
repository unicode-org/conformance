package org.unicode.conformance.messageformat2.icu75;

import static org.junit.Assert.assertEquals;

import com.ibm.icu.util.ULocale;
import java.util.ArrayList;
import java.util.List;
import java.util.Locale;
import java.util.TimeZone;
import org.junit.After;
import org.junit.Before;
import org.junit.Ignore;
import org.junit.Rule;
import org.junit.Test;
import org.junit.rules.TestName;
import org.unicode.conformance.testtype.messageformat2.IMFInputParam;
import org.unicode.conformance.testtype.messageformat2.MFInputParamDatetime;
import org.unicode.conformance.testtype.messageformat2.MFInputParamObject;
import org.unicode.conformance.testtype.messageformat2.MessageFormatInputJson;
import org.unicode.conformance.testtype.messageformat2.MessageFormatTester;

public class MessageFormatterTest {

  /**
   * The default locale used for all of our tests. Used in @Before
   */
  protected final static Locale defaultLocale = Locale.US;

  /**
   * The default time zone for all of our tests. Used in @Before
   */
  protected final static TimeZone defaultTimeZone = TimeZone.getTimeZone("America/Los_Angeles");

  private com.ibm.icu.util.TimeZone testStartDefaultIcuTz;

  private TimeZone testStartDefaultJdkTz;

  private ULocale testStartDefaultULocale;

  private Locale testStartDefaultLocale;

  @Rule
  public TestName name = new TestName();

  // Copying test setup behavior from ICU4J CoreTestFmwk / TestFmwk, which
  // ensures we pin the default locale and TZ during the test. ICU Formatters
  // implicitly use the system's default locale and TZ.
  @Before
  public final void setup() {
    // Just like TestFmwk initializes JDK TimeZone and Locale before every test,
    // do the same for ICU TimeZone and ULocale.
    ULocale.setDefault(ULocale.forLocale(defaultLocale));
    com.ibm.icu.util.TimeZone.setDefault(
        com.ibm.icu.util.TimeZone.getTimeZone(defaultTimeZone.getID()));

    // Save starting timezones
    testStartDefaultIcuTz = com.ibm.icu.util.TimeZone.getDefault();
    testStartDefaultJdkTz = TimeZone.getDefault();

    // Save starting locales
    testStartDefaultULocale = ULocale.getDefault();
    testStartDefaultLocale = Locale.getDefault();
  }

  // Copying test teardown beahvior from ICU4J CoreTestFmwk, corresponding to
  // the setup work.
  @After
  public final void teardown() {
    String testMethodName = name.getMethodName();

    // Assert that timezones are in a good state

    com.ibm.icu.util.TimeZone testEndDefaultIcuTz = com.ibm.icu.util.TimeZone.getDefault();
    TimeZone testEndDefaultJdkTz = TimeZone.getDefault();

    assertEquals("In [" + testMethodName + "] Test should keep in sync ICU & JDK TZs",
        testEndDefaultIcuTz.getID(),
        testEndDefaultJdkTz.getID());

    assertEquals("In [" + testMethodName + "] Test should reset ICU default TZ",
        testStartDefaultIcuTz.getID(), testEndDefaultIcuTz.getID());
    assertEquals("In [" + testMethodName + "] Test should reset JDK default TZ",
        testStartDefaultJdkTz.getID(), testEndDefaultJdkTz.getID());

    // Assert that locales are in a good state

    ULocale testEndDefaultULocale = ULocale.getDefault();
    Locale testEndDefaultLocale = Locale.getDefault();

    assertEquals("In [" + testMethodName + "] Test should reset ICU ULocale",
        testStartDefaultULocale.toLanguageTag(), testEndDefaultULocale.toLanguageTag());
    assertEquals("In [" + testMethodName + "] Test should reset JDK Locale",
        testStartDefaultLocale.toLanguageTag(), testEndDefaultLocale.toLanguageTag());
  }

  @Test
  public void testGetFormattedMessage() {
    // Setup
    MessageFormatInputJson inputJson = new MessageFormatInputJson();
    inputJson.label = "00001";
    inputJson.locale = "en-GB";
    inputJson.src = "Hello {$name}, your card expires on {$exp :datetime skeleton=yMMMdE}!";
    inputJson.test_description = "Test using the ICU4J API doc example for the MessageFormatter class";
    List<IMFInputParam> inputs = new ArrayList<>();
    MFInputParamObject nameArg = new MFInputParamObject();
    nameArg.name = "name";
    nameArg.value = "John";
    inputs.add(nameArg);
    MFInputParamDatetime expArg = new MFInputParamDatetime("exp", "2023-03-27T19:42:51"); // March 27, 2023, 7:42:51 PM
    expArg.name = "exp";
    inputs.add(expArg);
    inputJson.params = inputs;

    // Actual
    String formattedString = MessageFormatTester.INSTANCE.getFormattedMessage(inputJson);

    // Expect & assert test
    String expected = "Hello John, your card expires on 27/03/2023, 12:42!";
    assertEquals(expected, formattedString);

  }

  // ICU 75 impl output differs from MF2 spec defined at same time point (CLDR 45)
  // in what to return in message for non-provided args / formatting errors
  @Test
  public void testGetFormattedMessage_usingNonProvidedArg() {
    // Setup
    MessageFormatInputJson inputJson = new MessageFormatInputJson();
    inputJson.label = "00020";
    inputJson.locale = "en-US";
    inputJson.src = ":date";
    inputJson.test_description = "Test of formatting a pattern using an input arg that isn't provided";
    List<IMFInputParam> inputs = new ArrayList<>();
    inputJson.params = inputs;

    // Actual
    String formattedString = MessageFormatTester.INSTANCE.getFormattedMessage(inputJson);

    // Expect & assert test
    String expected = ":date";
    assertEquals(expected, formattedString);
  }

  @Test
  public void testGetFormattedMessage_numberLiteralOperand() {
    // Setup
    MessageFormatInputJson inputJson = new MessageFormatInputJson();
    inputJson.label = "00035";
    inputJson.locale = "en-US";
    inputJson.src = "hello {4.2 :integer}";
    inputJson.test_description = "Test of formatting a pattern using an input arg that isn't provided";
    List<IMFInputParam> inputs = new ArrayList<>();
    inputJson.params = inputs;

    // Actual
    String formattedString = MessageFormatTester.INSTANCE.getFormattedMessage(inputJson);

    // Expect & assert test
    String expected = "hello 4";
    assertEquals(expected, formattedString);
  }

}
