package org.unicode.conformance.testtype;

import org.unicode.conformance.ExecutorUtils;

public interface ITestType {

  default io.lacuna.bifurcan.Map<String,Object> parseInput(String inputLine) {
    return ExecutorUtils.parseInputLine(inputLine);
  }

  ITestTypeInputJson inputMapToJson(io.lacuna.bifurcan.Map<String,Object> inputMapData);

  default ITestTypeInputJson parseInputJson(String inputLine) {
    io.lacuna.bifurcan.Map<String,Object> inputMapData =
        parseInput(inputLine);
    ITestTypeInputJson inputJson = inputMapToJson(inputMapData);

    return inputJson;
  }

  ITestTypeOutputJson execute(ITestTypeInputJson inputJson);

  ITestTypeOutputJson getDefaultOutputJson();

  io.lacuna.bifurcan.IMap<String,Object> convertOutputToMap(ITestTypeOutputJson outputJson);

  String formatOutputJson(ITestTypeOutputJson outputJson);

  default ITestTypeOutputJson getStructuredOutputFromInputStr(String inputLine) {
    io.lacuna.bifurcan.Map<String,Object> inputMapData = parseInput(inputLine);
    return getStructuredOutputFromInput(inputMapData);
  }

  default ITestTypeOutputJson getStructuredOutputFromInput(io.lacuna.bifurcan.Map<String,Object> inputMapData) {
    ITestTypeInputJson inputJson = inputMapToJson(inputMapData);
    ITestTypeOutputJson outputJson = execute(inputJson);
    return outputJson;
  }

  default String getFinalOutputFromInput(io.lacuna.bifurcan.Map<String,Object> inputMapData) throws Exception {
    ITestTypeOutputJson outputJson = getStructuredOutputFromInput(inputMapData);
    String formattedOutput = formatOutputJson(outputJson);
    return formattedOutput;
  }

}
