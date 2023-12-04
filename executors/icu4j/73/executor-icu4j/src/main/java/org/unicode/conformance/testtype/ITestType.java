package org.unicode.conformance.testtype;

import org.unicode.conformance.ExecutorUtils;

public interface ITestType {

  default io.lacuna.bifurcan.Map<String,String> parseInput(String inputLine) {
    return ExecutorUtils.parseInputLine(inputLine);
  }

  ITestTypeInputJson inputMapToJson(io.lacuna.bifurcan.Map<String,String> inputMapData);

  default ITestTypeInputJson parseInputJson(String inputLine) {
    io.lacuna.bifurcan.Map<String,String> inputMapData =
        parseInput(inputLine);
      ITestTypeInputJson inputJson = inputMapToJson(inputMapData);

      return inputJson;
  }

  ITestTypeOutputJson execute(ITestTypeInputJson inputJson);

  String formatOutputJson(ITestTypeOutputJson outputJson);

  default ITestTypeOutputJson getStructuredOutputFromInput(String inputLine) {
    ITestTypeInputJson inputJson = parseInputJson(inputLine);
    ITestTypeOutputJson outputJson = execute(inputJson);
    return outputJson;
  }

  default String getFinalOutputFromInput(String inputLine) throws Exception {
    ITestTypeOutputJson outputJson = getStructuredOutputFromInput(inputLine);
    String formattedOutput = formatOutputJson(outputJson);
    return formattedOutput;
  }

}
