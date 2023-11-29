package org.unicode.conformance.testtype;

import com.google.gson.Gson;
import org.unicode.conformance.ExecutorUtils;

public class CollatorTester implements ITestType {

  @Override
  public ITestTypeInputJson parseInputJson(String inputLine) {
    return ExecutorUtils.GSON.fromJson(inputLine, CollatorInputJson.class);
  }

  @Override
  public ITestTypeOutputJson computeOutputJson(ITestTypeInputJson inputJson) {
    throw new RuntimeException("unimplemented!");
  }

  @Override
  public String formatOutputJson(ITestTypeOutputJson outputJson) {
    return ExecutorUtils.GSON.toJson(outputJson);
  }
}
