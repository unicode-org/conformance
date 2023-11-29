package org.unicode.conformance;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;

/**
 * Hello world!
 *
 */
public class Icu4jExecutor {

    /**
     * Entry point for the executor
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
        } catch (IOException ioe) {
            // At this level, we assume the IOException is coming from BufferedReader.
            // Any test case execution errors should be handled higher in the call stack (deeper in
            // the code)
            String javaErrorMsg = ioe.getMessage();
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
    public static String computeResponseString(String inputLine) {
        if (inputLine.equals("#EXIT")) {
            return null;
        } else if (inputLine.trim().equals("")) {
            return "";
        } else {
            return getTestCaseResponse(inputLine);
        }
    }

    public static String getTestCaseResponse(String inputLine) {
        throw new RuntimeException("Unimplemented!");
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
