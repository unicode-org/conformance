package org.unicode.conformance.testtype;

public interface ITestType {

  ITestTypeInputJson parseInputJson(String inputLine);

  ITestTypeOutputJson computeOutputJson(ITestTypeInputJson inputJson) throws Exception;

  String formatOutputJson(ITestTypeOutputJson outputJson);

  default ITestTypeOutputJson getStructuredOutputFromInput(String inputLine) throws Exception {
    ITestTypeInputJson inputJson = parseInputJson(inputLine);
    ITestTypeOutputJson outputJson = computeOutputJson(inputJson);
    return outputJson;
  }

  default String getFinalOutputFromInput(String inputLine) throws Exception {
    ITestTypeOutputJson outputJson = getStructuredOutputFromInput(inputLine);
    String formattedOutput = formatOutputJson(outputJson);
    return formattedOutput;
  }

}
