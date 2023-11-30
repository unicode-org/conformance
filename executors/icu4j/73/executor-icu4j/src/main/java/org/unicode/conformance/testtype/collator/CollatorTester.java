package org.unicode.conformance.testtype.collator;

import org.unicode.conformance.ExecutorUtils;
import org.unicode.conformance.testtype.ITestType;
import org.unicode.conformance.testtype.ITestTypeInputJson;
import org.unicode.conformance.testtype.ITestTypeOutputJson;

public class CollatorTester implements ITestType {

  public static CollatorTester INSTANCE = new CollatorTester();

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
    return ExecutorUtils.GSON.toJson((CollatorOutputJson) outputJson);
  }
}
