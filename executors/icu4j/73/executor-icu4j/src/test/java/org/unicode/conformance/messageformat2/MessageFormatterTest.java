package org.unicode.conformance.messageformat2;

import static org.junit.Assert.assertEquals;

import java.util.ArrayList;
import java.util.Date;
import java.util.List;
import org.junit.Test;
import org.unicode.conformance.testtype.messageformat2.MFInputArg;
import org.unicode.conformance.testtype.messageformat2.MFInputArgType;
import org.unicode.conformance.testtype.messageformat2.MFTestSubType;
import org.unicode.conformance.testtype.messageformat2.MessageFormatInputJson;
import org.unicode.conformance.testtype.messageformat2.MessageFormatTester;

public class MessageFormatterTest {

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
    expArg.value = new Date(1679971371000L);  // March 27, 2023, 7:42:51 PM
    inputs.add(expArg);
    inputJson.inputs = inputs;

    // Actual
    String formattedString = MessageFormatTester.INSTANCE.getFormattedMessage(inputJson);

    // Expect & assert test
    String expected = "Hello John, your card expires on Mon, 27 Mar 2023!";
    assertEquals(expected, formattedString);

  }

}
