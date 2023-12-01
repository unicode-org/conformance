package org.unicode.conformance.testtype;

public interface ITestType {

  ITestTypeInputJson parseInputJson(String inputLine);

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
