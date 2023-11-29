package org.unicode.conformance;

import com.google.gson.Gson;

public class ExecutorUtils {

  public static Gson GSON = new Gson();

  public static void printResponseString(String responseString) {
    System.out.println(responseString);
  }

}
