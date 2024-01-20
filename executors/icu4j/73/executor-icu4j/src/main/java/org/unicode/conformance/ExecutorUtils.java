package org.unicode.conformance;

import com.google.gson.Gson;
import com.google.gson.reflect.TypeToken;
import io.lacuna.bifurcan.IEntry;
import java.util.HashMap;
import java.util.Iterator;
import java.util.Map;

public class ExecutorUtils {

  public static Gson GSON = new Gson();

  public static void printResponseString(String responseString) {
    System.out.println(responseString);
  }

  public static io.lacuna.bifurcan.Map<String,String> parseInputLine(String inputLine) {
    Map<String,String> parsedInputJavaMap = stringMapFromString(inputLine);

    io.lacuna.bifurcan.Map<String,String> parsedInputPersistentMap =
        io.lacuna.bifurcan.Map.from(parsedInputJavaMap);

    return parsedInputPersistentMap;
  }

  public static String formatAsJson(io.lacuna.bifurcan.IMap<String,String> mapData) {
    java.util.Map<String,String> jMap = new HashMap<>();
    for (Iterator<IEntry<String, String>> it = mapData.stream().iterator(); it.hasNext(); ) {
      IEntry<String, String> entry = it.next();
      jMap.put(entry.key(), entry.value());
    }
    return GSON.toJson(jMap);
  }

  public static Map<String,String> stringMapFromString(String s) {
    TypeToken<Map<String, String>> mapType = new TypeToken<Map<String, String>>(){};
    Map<String,String> parsedInputJavaMap = ExecutorUtils.GSON.fromJson(s, mapType);

    return parsedInputJavaMap;
  }

}
