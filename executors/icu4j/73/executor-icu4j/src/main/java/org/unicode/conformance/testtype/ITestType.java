package org.unicode.conformance.testtype;

public interface ITestType {

  ITestTypeInputJson parseInputJson(String inputLine);

  ITestTypeOutputJson computeOutputJson(ITestTypeInputJson inputJson);

  String formatOutputJson(ITestTypeOutputJson outputJson);

  default String getFinalOutputFromInput(String inputLine) {
    ITestTypeInputJson inputJson = parseInputJson(inputLine);
    ITestTypeOutputJson outputJson = computeOutputJson(inputJson);
    String formattedOutput = formatOutputJson(outputJson);
    return formattedOutput;
  }

}
