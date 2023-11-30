package org.unicode.conformance;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertFalse;
import static org.junit.Assert.assertNotNull;
import static org.junit.Assert.assertTrue;

import org.junit.Test;
import org.unicode.conformance.testtype.collator.CollatorInputJson;
import org.unicode.conformance.testtype.collator.CollatorOutputJson;
import org.unicode.conformance.testtype.collator.CollatorTester;

/**
 * Unit test for simple App.
 */
public class Icu4jExecutorTest 
{
    //
    // tests
    //

    @Test
    public void testParseSimpleJsonInput() {
        String testInput =
            "{\"test_type\": \"coll_shift_short\", \"label\": \"COLL_ABC1\", \"s1\": \"de\", \"s2\" : \"da\"}";
        CollatorInputJson input = (CollatorInputJson) CollatorTester.INSTANCE.parseInputJson(testInput);

        assertEquals(input.test_type, "coll_shift_short");
        assertEquals(input.label, "COLL_ABC1");
        assertEquals(input.s1, "de");
        assertEquals(input.s2, "da");
    }

    @Test
    public void testFormatSimpleJsonOutput() {
        CollatorOutputJson output = new CollatorOutputJson();

        output.test_type = "coll_shift_short";
        output.label = "COLL_ABC1";
        output.s1 = "de";
        output.s2 = "da";

        String expected =
            "{\"test_type\": \"coll_shift_short\", \"label\": \"COLL_ABC1\", \"s1\": \"de\", \"s2\" : \"da\"}";

        String formattedOutput = CollatorTester.INSTANCE.formatOutputJson(output);

        assertNotNull(formattedOutput);
    }

    @Test
    public void testSimpleJsonInputRoundTrip() {
        String testInput =
            "{\"test_type\": \"coll_shift_short\", \"label\": \"COLL_ABC1\", \"s1\": \"de\", \"s2\" : \"da\"}";
        CollatorInputJson input = ExecutorUtils.GSON.fromJson(testInput, CollatorInputJson.class);
        String formattedString = ExecutorUtils.GSON.toJson(input);
        CollatorInputJson reparsedInput = ExecutorUtils.GSON.fromJson(formattedString, CollatorInputJson.class);
        String reformattedString = ExecutorUtils.GSON.toJson(reparsedInput);

        assertEquals("Canonical JSON string should round trip",
            formattedString,
            reformattedString);
    }

    @Test
    public void testBasicTestCase() throws Exception {
        String testInput =
            "{\n"
            + "  \"label\": \"0151240\",\n"
            + "  \"string1\": \"ꌌ?\",\n"
            + "  \"string2\": \"ꌌa\"\n"
            + "}";
        CollatorOutputJson output =
            (CollatorOutputJson) CollatorTester.INSTANCE.getStructuredOutputFromInput(testInput);

        assertTrue(output.result);
    }

    @Test
    public void testBasicTestCase_negativeTestFailure() throws Exception {
        String testInput =
            "{\n"
                + "  \"label\": \"0151240\",\n"
                + "  \"string2\": \"ꌌ?\",\n"
                + "  \"string1\": \"ꌌa\"\n"
                + "}";
        CollatorOutputJson output =
            (CollatorOutputJson) CollatorTester.INSTANCE.getStructuredOutputFromInput(testInput);

        assertFalse(output.result);
    }
}
