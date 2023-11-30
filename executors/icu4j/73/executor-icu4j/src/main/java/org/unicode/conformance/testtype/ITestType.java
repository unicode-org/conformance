package org.unicode.conformance.testtype;

public interface ITestType {

  ITestTypeInputJson parseInputJson(String inputLine);

  ITestTypeOutputJson computeOutputJson(ITestTypeInputJson inputJson) throws Exception;

  String formatOutputJson(ITestTypeOutputJson outputJson);

  default String getFinalOutputFromInput(String inputLine) throws Exception {
    ITestTypeInputJson inputJson = parseInputJson(inputLine);
    ITestTypeOutputJson outputJson = computeOutputJson(inputJson);
    String formattedOutput = formatOutputJson(outputJson);
    return formattedOutput;
  }

}
