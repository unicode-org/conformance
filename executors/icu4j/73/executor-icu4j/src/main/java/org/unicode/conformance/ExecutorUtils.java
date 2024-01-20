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

  public static io.lacuna.bifurcan.Map<String,Object> parseInputLine(String inputLine) {
    Map<String,Object> parsedInputJavaMap = stringMapFromString(inputLine);

    io.lacuna.bifurcan.Map<String,Object> parsedInputPersistentMap =
        io.lacuna.bifurcan.Map.from(parsedInputJavaMap);

    return parsedInputPersistentMap;
  }

  public static String formatAsJson(io.lacuna.bifurcan.IMap<String,Object> mapData) {
    java.util.Map<String,Object> jMap = new HashMap<>();
    for (Iterator<IEntry<String, Object>> it = mapData.stream().iterator(); it.hasNext(); ) {
      IEntry<String, Object> entry = it.next();
      jMap.put(entry.key(), entry.value());
    }
    return GSON.toJson(jMap);
  }

  public static Map<String,Object> stringMapFromString(String s) {
    TypeToken<Map<String, Object>> mapType = new TypeToken<Map<String, Object>>(){};
    Map<String,Object> parsedInputJavaMap = ExecutorUtils.GSON.fromJson(s, mapType);

    return parsedInputJavaMap;
  }

}
