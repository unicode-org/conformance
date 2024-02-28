package org.unicode.conformance.messageformat2;

import static org.junit.Assert.assertEquals;

import com.ibm.icu.util.ULocale;
import java.util.ArrayList;
import java.util.Date;
import java.util.List;
import java.util.Locale;
import java.util.TimeZone;
import org.junit.After;
import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.junit.rules.TestName;
import org.unicode.conformance.testtype.messageformat2.MFInputArg;
import org.unicode.conformance.testtype.messageformat2.MFInputArgType;
import org.unicode.conformance.testtype.messageformat2.MFTestSubType;
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

  private java.util.TimeZone testStartDefaultJdkTz;

  private com.ibm.icu.util.ULocale testStartDefaultULocale;

  private java.util.Locale testStartDefaultLocale;

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
    testStartDefaultJdkTz = java.util.TimeZone.getDefault();

    // Save starting locales
    testStartDefaultULocale = com.ibm.icu.util.ULocale.getDefault();
    testStartDefaultLocale = java.util.Locale.getDefault();
  }

  // Copying test teardown beahvior from ICU4J CoreTestFmwk, corresponding to
  // the setup work.
  @After
  public final void teardown() {
    String testMethodName = name.getMethodName();

    // Assert that timezones are in a good state

    com.ibm.icu.util.TimeZone testEndDefaultIcuTz = com.ibm.icu.util.TimeZone.getDefault();
    java.util.TimeZone testEndDefaultJdkTz = java.util.TimeZone.getDefault();

    assertEquals("In [" + testMethodName + "] Test should keep in sync ICU & JDK TZs",
        testEndDefaultIcuTz.getID(),
        testEndDefaultJdkTz.getID());

    assertEquals("In [" + testMethodName + "] Test should reset ICU default TZ",
        testStartDefaultIcuTz.getID(), testEndDefaultIcuTz.getID());
    assertEquals("In [" + testMethodName + "] Test should reset JDK default TZ",
        testStartDefaultJdkTz.getID(), testEndDefaultJdkTz.getID());

    // Assert that locales are in a good state

    com.ibm.icu.util.ULocale testEndDefaultULocale = com.ibm.icu.util.ULocale.getDefault();
    java.util.Locale testEndDefaultLocale = java.util.Locale.getDefault();

    assertEquals("In [" + testMethodName + "] Test should reset ICU ULocale",
        testStartDefaultULocale.toLanguageTag(), testEndDefaultULocale.toLanguageTag());
    assertEquals("In [" + testMethodName + "] Test should reset JDK Locale",
        testStartDefaultLocale.toLanguageTag(), testEndDefaultLocale.toLanguageTag());
  }

  @Test
  public void testGetFormattedMessage() {
    // Setup
    MessageFormatInputJson inputJson = new MessageFormatInputJson();
    inputJson.test_type = "message_fmt2";
    inputJson.label = "00001";
    inputJson.test_subtype = MFTestSubType.formatter;
    inputJson.locale = "en-GB";
    inputJson.pattern = "{Hello {$name}, your card expires on {$exp :datetime skeleton=yMMMdE}!}";
    inputJson.test_description = "Test using the ICU4J API doc example for the MessageFormatter class";
    List<MFInputArg> inputs = new ArrayList<>();
    MFInputArg nameArg = new MFInputArg();
    nameArg.name = "name";
    nameArg.argType = MFInputArgType.string;
    nameArg.value = "John";
    inputs.add(nameArg);
    MFInputArg expArg = new MFInputArg();
    expArg.name = "exp";
    expArg.argType = MFInputArgType.datetime;
    expArg.value = new Date(2023 - 1900, 2, 27, 19, 42, 51);  // March 27, 2023, 7:42:51 PM
    inputs.add(expArg);
    inputJson.inputs = inputs;

    // Actual
    String formattedString = MessageFormatTester.INSTANCE.getFormattedMessage(inputJson);

    // Expect & assert test
    String expected = "Hello John, your card expires on Mon, 27 Mar 2023!";
    assertEquals(expected, formattedString);

  }

}
