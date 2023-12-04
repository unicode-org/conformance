package org.unicode.conformance;

import com.google.gson.Gson;
import com.google.gson.reflect.TypeToken;
import java.util.Map;

public class ExecutorUtils {

  public static Gson GSON = new Gson();

  public static void printResponseString(String responseString) {
    System.out.println(responseString);
  }

  public static io.lacuna.bifurcan.Map<String,String> parseInputLine(String inputLine) {
    TypeToken<Map<String, String>> mapType = new TypeToken<Map<String, String>>(){};
    Map<String,String> parsedInputJavaMap = ExecutorUtils.GSON.fromJson(inputLine, mapType);

    io.lacuna.bifurcan.Map<String,String> parsedInputPersistentMap =
        io.lacuna.bifurcan.Map.from(parsedInputJavaMap);

    return parsedInputPersistentMap;
  }

}
