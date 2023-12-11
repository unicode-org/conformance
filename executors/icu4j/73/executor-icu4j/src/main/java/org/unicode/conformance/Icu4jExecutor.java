package org.unicode.conformance;

import com.google.gson.reflect.TypeToken;
import com.ibm.icu.impl.locale.XCldrStub.ImmutableMap;
import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.util.HashMap;
import java.util.Map;
import java.util.Optional;
import org.unicode.conformance.testtype.ITestType;
import org.unicode.conformance.testtype.collator.CollatorTester;

/**
 * Hello world!
 *
 */
public class Icu4jExecutor {

    public static final String PLATFORM_VERSION = "73.2";
    public static final String ICU_VERSION = "73";

    public static final String CLDR_VERSION = "43";

    /**
     * Entry point for the executor.
     *
     * Run on an infinite loop until the input "#EXIT" is received.
     */
    public static void main(String[] args) throws IOException {
        try (InputStreamReader isr = new InputStreamReader(System.in);
             BufferedReader br = new BufferedReader(isr)) {
            while (true) {
                computeAndHandleResponse(br);
            }
        } catch (IOException ioe) {
            String javaSetupErrorMsg = ioe.getMessage();
            String executorErrorMsg = "! " + javaSetupErrorMsg;
            ExecutorUtils.printResponseString(executorErrorMsg);

            // exit with non-zero return code
            throw ioe;
        }
    }

    public static void computeAndHandleResponse(BufferedReader br) {
        try {
            String line = br.readLine();
            String response = computeResponseString(line);
            handleResponseString(response);
        } catch (Exception e) {
            // At this level, we assume the IOException is coming from BufferedReader.
            // Any test case execution errors should be handled higher in the call stack (deeper in
            // the code)
            String javaErrorMsg = e.getMessage();
            String executorErrorMsg = "! " + javaErrorMsg;
            ExecutorUtils.printResponseString(executorErrorMsg);
        }
    }

    /**
     * Returns the string to be sent back to the testdriver caller, with the following cases:
     *
     * <ul>
     *   <li>For a test case input that was executed, return the JSON string of the result</li>
     *   <li>For empty input lines, return the empty string</li>
     *   <li>For end-of-input when <pre>#EXIT</pre> is sent in as input, return null</li>
     *   <li>For errors during test execution, return the error output string prefixed with
     *   <pre>#</pre></li>
     * </ul>
     */
    public static String computeResponseString(String inputLine) throws Exception {
        if (inputLine.equals("#EXIT")) {
            return null;
        } else if (inputLine.trim().equals("")) {
            return "";
        } else if (inputLine.equals("#VERSION")) {
            return getVersionResponse();
        } else {
            return getTestCaseResponse(inputLine);
        }
    }

    public static String getVersionResponse() {
        Map<String,String> versionMap = new HashMap<>();
        versionMap.put("cldrVersion", CLDR_VERSION);
        versionMap.put("icuVersion", ICU_VERSION);
        versionMap.put("platformVersion", PLATFORM_VERSION);

        String result = ExecutorUtils.GSON.toJson(versionMap);
        return result;
    }

    public static String getTestCaseResponse(String inputLine) throws Exception {

        io.lacuna.bifurcan.Map<String,String> parsedInputPersistentMap =
            ExecutorUtils.parseInputLine(inputLine);

        Optional<String> testTypeOpt = parsedInputPersistentMap.get("test_type");

        if (!testTypeOpt.isPresent()) {
            io.lacuna.bifurcan.IMap<String,String> response =
                parsedInputPersistentMap
                    .put("error", "Error in input")
                    .put("error_msg", "Error in input found in executor before execution");

            return ExecutorUtils.formatAsJson(response);
        } else {
            String testTypeStr = testTypeOpt.get();
            ITestType testType;
            if (testTypeStr.equals("collate_short")) {
                testType = new CollatorTester();
            } else {
                io.lacuna.bifurcan.IMap<String,String> response =
                    parsedInputPersistentMap
                        .put("error", "Error in input")
                        .put("error_msg", "Error in input found in executor before execution");

                return ExecutorUtils.formatAsJson(response);
            }

            return testType.getFinalOutputFromInput(parsedInputPersistentMap);
        }
    }

    /**
     * Perform behavior according to the executor spec at <code>REPO/executors/README.md</code>
     * based on the output and associated semantics of <code>computeResponseString()</code>.
     * @param responseString
     */
    public static void handleResponseString(String responseString) {
        if (responseString == null) {
            System.exit(0);
        }
        if (responseString.equals("")) {
            return; // empty input line, do nothing
        }

        // otherwise, response string carries test result
        ExecutorUtils.printResponseString(responseString);
    }

}
